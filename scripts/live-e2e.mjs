import { createHash } from "node:crypto";
import { mkdirSync, writeFileSync } from "node:fs";
import { createInterface } from "node:readline";
import { createAccount, createClient } from "genlayer-js";
import { studionet } from "genlayer-js/chains";

const CONTRACT = "0x89c65F2c7999CC55Ee8E21A35768CD9B1269e956";
const CERT_URL = "https://raw.githubusercontent.com/eaglebooth/CalScope/e0805c2361acecee24127176e0a15c3a52fe47d7/fixtures/CERTIFICATE.md";
const REQUIREMENT_URL = "https://raw.githubusercontent.com/eaglebooth/ClaimAnchor/b91162fe9973e252ca9016430893d4c7b19d6296/CALSCOPE_REQUIREMENT_JOB_204.md";
const CERT_SHA = "54bcaba189b96b90004c31c98cce27dec2477a0155ccc7908391491fdc764cf7";
const REQUIREMENT_SHA = "c091dd2a343f46c36e529e8057dde8572d8c278594fc3ffa5ba2ca9316ca66e3";

async function readKeys() {
  const rl = createInterface({ input: process.stdin, terminal: false });
  const lines = [];
  return await new Promise((resolve, reject) => {
    rl.on("line", line => {
      if (line.trim()) lines.push(line.trim().replace(/^0x/, ""));
      if (lines.length === 2) { rl.close(); resolve(lines); }
    });
    rl.on("close", () => { if (lines.length < 2) reject(new Error("Two wallet keys are required on stdin")); });
  });
}

const [keyA, keyB] = await readKeys();
const walletA = createAccount(`0x${keyA}`), walletB = createAccount(`0x${keyB}`);
const clientA = createClient({ chain: studionet, account: walletA });
const clientB = createClient({ chain: studionet, account: walletB });
const report = {
  contract: CONTRACT,
  network: "GenLayer Studionet 61999",
  sourceCommit: "e0805c2361acecee24127176e0a15c3a52fe47d7",
  actors: { calibrator: walletA.address, facilityQaAndOperator: walletB.address },
  sources: {
    certificate: { url: CERT_URL, sha256: CERT_SHA, bytes: 443 },
    requirement: { url: REQUIREMENT_URL, sha256: REQUIREMENT_SHA, bytes: 673 }
  },
  transactions: [], assertions: [], final: {}
};

mkdirSync("docs/live-evidence", { recursive: true });
const save = () => writeFileSync("docs/live-evidence/studionet-run.json", `${JSON.stringify(report, null, 2)}\n`);
const check = (condition, label, details = {}) => {
  report.assertions.push({ label, pass: Boolean(condition), details }); save();
  if (!condition) throw new Error(`Assertion failed: ${label} ${JSON.stringify(details)}`);
};
const read = async (method, args = []) => JSON.parse(await clientA.readContract({ address: CONTRACT, functionName: method, args }));
const execution = tx => {
  const validators = tx.consensus_data?.validators || [];
  if (validators.some(v => v.vote === "agree" && v.execution_result === "SUCCESS")) return "SUCCESS";
  if (validators.some(v => v.vote === "agree" && v.execution_result === "ERROR")) return "ERROR";
  const leader = tx.consensus_data?.leader_receipt?.[0]?.genvm_result;
  return leader && !leader.error_code ? "SUCCESS" : leader?.error_code ? "ERROR" : "UNKNOWN";
};
const write = async (label, client, method, args, expected = "SUCCESS") => {
  let hash;
  try {
    hash = await client.writeContract({ address: CONTRACT, functionName: method, args, value: 0n });
  } catch (error) {
    if (expected !== "ERROR") throw error;
    report.transactions.push({ label, method, expected, hash: null, status: "PRECHECK_REJECTED", execution: "ERROR", error: String(error) });
    save(); return null;
  }
  process.stdout.write(`${label}: ${hash}\n`);
  let tx = {};
  for (let i = 0; i < 360; i++) {
    tx = await client.getTransaction({ hash });
    if (["FINALIZED", "CANCELED", "UNDETERMINED"].includes(tx.statusName)) break;
    await new Promise(resolve => setTimeout(resolve, 2500));
  }
  const result = execution(tx);
  report.transactions.push({ label, method, expected, hash, status: tx.statusName || "UNKNOWN", execution: result }); save();
  check(tx.statusName === "FINALIZED" && result === expected, `${label} finalized with ${expected}`, { hash, status: tx.statusName, execution: result });
  return hash;
};
const contractHash = value => createHash("sha256").update(JSON.stringify(value, Object.keys(value).sort(), 0)).digest("hex");

const version = await read("get_contract_version");
check(version.name === "CalScope" && version.version === 1, "deployed CalScope V1", version);
check(walletA.address.toLowerCase() === "0xeb57bc7125fa60d7482ce12058397369ab3581f8", "wallet A is registered calibrator", { address: walletA.address });
check(walletB.address.toLowerCase() === "0x2da5393d7bbb9a037dc3abb56dbbc5c150fc843f", "wallet B is registered facility QA", { address: walletB.address });

await write("reject unregistered certificate issuer", clientB, "issue_certificate", ["CAL-UNAUTHORIZED", "BAL-17", CERT_URL, CERT_SHA, 443n], "ERROR");
await write("issue authenticated certificate", clientA, "issue_certificate", ["CAL-2026-017", "BAL-17", CERT_URL, CERT_SHA, 443n]);
await write("reject wrong facility QA", clientA, "seal_requirement", ["north-lab", "JOB-WRONG-QA", walletB.address, "BAL-17", REQUIREMENT_URL, REQUIREMENT_SHA, 673n], "ERROR");
await write("seal authenticated requirement", clientB, "seal_requirement", ["north-lab", "JOB-204", walletB.address, "BAL-17", REQUIREMENT_URL, REQUIREMENT_SHA, 673n]);

const certificate = await read("get_certificate", [walletA.address, "CAL-2026-017"]);
const requirement = await read("get_requirement", ["north-lab", "JOB-204"]);
check(certificate.exists && certificate.active && certificate.evidence_sha256 === CERT_SHA, "certificate canonical readback", certificate);
check(requirement.exists && requirement.operator.toLowerCase() === walletB.address.toLowerCase(), "requirement canonical readback", requirement);

await write("assess applicability", clientA, "assess", [walletA.address, "CAL-2026-017", "north-lab", "JOB-204"]);
const assessmentPayload = {
  certificate: `${walletA.address.toLowerCase()}:CAL-2026-017`, certificate_revision: 1,
  domain: "CALSCOPE_ASSESSMENT_ID_V1", requirement: "north-lab:JOB-204", requirement_revision: 1
};
const assessmentId = contractHash(assessmentPayload);
const assessment = await read("get_assessment", [assessmentId]);
check(assessment.exists && assessment.verdict === "APPLICABLE" && Boolean(assessment.authorization_id), "consensus created applicable authorization", assessment);

await write("reject wrong operator", clientA, "consume_authorization", [assessment.authorization_id], "ERROR");
await write("consume authorization once", clientB, "consume_authorization", [assessment.authorization_id]);
await write("reject authorization replay", clientB, "consume_authorization", [assessment.authorization_id], "ERROR");
const authorization = await read("get_authorization", [assessment.authorization_id]);
const stats = await read("get_stats");
check(authorization.exists && authorization.consumed && authorization.receipt.length === 64, "authorization consumed with receipt", authorization);
check(stats.certificates === 1 && stats.requirements === 1 && stats.assessments === 1 && stats.consumed === 1, "canonical final counters", stats);
report.final = { version, certificate, requirement, assessment, authorization, stats };
save();
process.stdout.write(`${JSON.stringify(report, null, 2)}\n`);
