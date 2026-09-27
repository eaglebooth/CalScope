import hashlib, json, pytest

def addr(value): return "0x" + bytes(value).hex()
def sha(text): return hashlib.sha256(text.encode()).hexdigest()

COMMIT = "1" * 40
CERT = """# Calibration certificate CAL-2026-017
Issuer: MetroCal Laboratory
Device serial: BAL-17
Quantity: mass
Calibrated range: 0 g to 5000 g
Expanded uncertainty: 0.20 g
Method: ISO 17025 mass calibration procedure MC-04
Environmental scope: 20 C to 25 C, relative humidity 30% to 60%
Status: valid and not revoked
"""
REQ = """# Measurement requirement JOB-204
Facility: North Lab
Device serial: BAL-17
Quantity: mass
Operating range: 100 g to 4000 g
Maximum permitted uncertainty: 0.50 g
Required method: ISO 17025 traceable mass calibration
Environment: 22 C and 45% relative humidity
Operator must hold the exact one-time authorization for JOB-204.
"""
CERT_URL = f"https://raw.githubusercontent.com/calibrator/certificates/{COMMIT}/CAL-2026-017.md"
REQ_URL = f"https://raw.githubusercontent.com/facility/requirements/{COMMIT}/JOB-204.md"

def setup(c, vm, owner, calibrator, qa, operator):
    c.set_calibrator(addr(calibrator), "calibrator/certificates", True)
    c.set_facility("north-lab", addr(qa), "facility/requirements", True)
    with vm.prank(calibrator):
        c.issue_certificate("CAL-2026-017", "BAL-17", CERT_URL, sha(CERT), len(CERT.encode()))
    with vm.prank(qa):
        c.seal_requirement("north-lab", "JOB-204", addr(operator), "BAL-17", REQ_URL, sha(REQ), len(REQ.encode()))

def mock_assessment(vm, verdict="APPLICABLE", certificate=CERT, requirement=REQ):
    vm.mock_web(r"CAL-2026-017.md", {"method":"GET","status":200,"body":certificate})
    vm.mock_web(r"JOB-204.md", {"method":"GET","status":200,"body":requirement})
    vm.mock_llm(r"Evaluate whether an authenticated calibration certificate", json.dumps({"verdict":verdict}))

def assessed(c, vm, owner, calibrator, qa, operator, verdict="APPLICABLE"):
    setup(c,vm,owner,calibrator,qa,operator); mock_assessment(vm,verdict)
    assert c.assess(addr(calibrator),"CAL-2026-017","north-lab","JOB-204") == verdict
    # Derive the ID from the persisted assessment rather than duplicating contract hashing rules.
    cert_key = addr(calibrator).lower() + ":CAL-2026-017"
    req_key = "north-lab:JOB-204"
    payload = {"certificate":cert_key,"certificate_revision":1,"domain":"CALSCOPE_ASSESSMENT_ID_V1","requirement":req_key,"requirement_revision":1}
    assessment_id = hashlib.sha256(json.dumps(payload,sort_keys=True,separators=(",",":"),ensure_ascii=True).encode()).hexdigest()
    return json.loads(c.get_assessment(assessment_id)), assessment_id

def test_schema_and_registry_authority(direct_deploy,direct_vm,direct_owner,direct_alice):
    c=direct_deploy("contracts/calscope.py")
    assert json.loads(c.get_contract_version())["schema"] == "calibration-applicability-capability-v1"
    with direct_vm.prank(direct_alice), direct_vm.expect_revert("REGISTRY_AUTHORITY_REQUIRED"):
        c.set_calibrator(addr(direct_alice),"calibrator/certificates",True)

def test_only_registered_evidence_authorities_can_issue(direct_deploy,direct_vm,direct_alice,direct_bob):
    c=direct_deploy("contracts/calscope.py")
    with direct_vm.prank(direct_alice), direct_vm.expect_revert("APPROVED_CALIBRATOR_REQUIRED"):
        c.issue_certificate("CAL-2026-017","BAL-17",CERT_URL,sha(CERT),len(CERT.encode()))
    c.set_facility("north-lab",addr(direct_alice),"facility/requirements",True)
    with direct_vm.prank(direct_bob), direct_vm.expect_revert("FACILITY_QA_REQUIRED"):
        c.seal_requirement("north-lab","JOB-204",addr(direct_bob),"BAL-17",REQ_URL,sha(REQ),len(REQ.encode()))

def test_repository_scope_and_device_binding(direct_deploy,direct_vm,direct_owner,direct_alice,direct_bob):
    c=direct_deploy("contracts/calscope.py")
    c.set_calibrator(addr(direct_alice),"calibrator/certificates",True)
    with direct_vm.prank(direct_alice), direct_vm.expect_revert("INVALID_CERTIFICATE_URL"):
        c.issue_certificate("CAL-2026-017","BAL-17",REQ_URL,sha(CERT),len(CERT.encode()))
    c.set_facility("north-lab",addr(direct_bob),"facility/requirements",True)
    with direct_vm.prank(direct_alice): c.issue_certificate("CAL-2026-017","BAL-17",CERT_URL,sha(CERT),len(CERT.encode()))
    with direct_vm.prank(direct_bob): c.seal_requirement("north-lab","JOB-204",addr(direct_bob),"BAL-99",REQ_URL,sha(REQ),len(REQ.encode()))
    with direct_vm.expect_revert("DEVICE_SERIAL_MISMATCH"):
        c.assess(addr(direct_alice),"CAL-2026-017","north-lab","JOB-204")

@pytest.mark.parametrize("verdict",["APPLICABLE","OUT_OF_SCOPE","CONDITIONAL","INSUFFICIENT_EVIDENCE"])
def test_bounded_verdicts_and_authorization_creation(direct_deploy,direct_vm,direct_owner,direct_alice,direct_bob,verdict):
    c=direct_deploy("contracts/calscope.py")
    state,_=assessed(c,direct_vm,direct_owner,direct_alice,direct_bob,direct_owner,verdict)
    if verdict == "INSUFFICIENT_EVIDENCE":
        assert state == {"exists":False}
    else:
        assert state["verdict"] == verdict and len(state["decision_digest"]) == 64
        assert bool(state["authorization_id"]) is (verdict == "APPLICABLE")

def test_integrity_failure_never_authorizes(direct_deploy,direct_vm,direct_owner,direct_alice,direct_bob):
    c=direct_deploy("contracts/calscope.py"); setup(c,direct_vm,direct_owner,direct_alice,direct_bob,direct_owner)
    direct_vm.mock_web(r"CAL-2026-017.md",{"method":"GET","status":200,"body":CERT+"changed"})
    direct_vm.mock_web(r"JOB-204.md",{"method":"GET","status":200,"body":REQ})
    assert c.assess(addr(direct_alice),"CAL-2026-017","north-lab","JOB-204") == "INSUFFICIENT_EVIDENCE"
    direct_vm.clear_mocks()
    mock_assessment(direct_vm,"APPLICABLE")
    assert c.assess(addr(direct_alice),"CAL-2026-017","north-lab","JOB-204") == "APPLICABLE"

def test_malformed_model_output_fails_closed(direct_deploy,direct_vm,direct_owner,direct_alice,direct_bob):
    c=direct_deploy("contracts/calscope.py"); setup(c,direct_vm,direct_owner,direct_alice,direct_bob,direct_owner)
    direct_vm.mock_web(r"CAL-2026-017.md",{"method":"GET","status":200,"body":CERT})
    direct_vm.mock_web(r"JOB-204.md",{"method":"GET","status":200,"body":REQ})
    direct_vm.mock_llm(r"Evaluate whether an authenticated calibration certificate",'{"verdict":"APPLICABLE","extra":true}')
    assert c.assess(addr(direct_alice),"CAL-2026-017","north-lab","JOB-204") == "INSUFFICIENT_EVIDENCE"

def test_only_operator_consumes_once(direct_deploy,direct_vm,direct_owner,direct_alice,direct_bob):
    c=direct_deploy("contracts/calscope.py")
    state,_=assessed(c,direct_vm,direct_owner,direct_alice,direct_bob,direct_owner)
    aid=state["authorization_id"]
    with direct_vm.prank(direct_alice), direct_vm.expect_revert("ASSIGNED_OPERATOR_REQUIRED"):
        c.consume_authorization(aid)
    receipt=c.consume_authorization(aid); assert len(receipt)==64
    assert json.loads(c.get_authorization(aid))["consumed"] is True
    with direct_vm.expect_revert("AUTHORIZATION_ALREADY_CONSUMED"): c.consume_authorization(aid)

def test_revocation_invalidates_unconsumed_authorization(direct_deploy,direct_vm,direct_owner,direct_alice,direct_bob):
    c=direct_deploy("contracts/calscope.py")
    state,_=assessed(c,direct_vm,direct_owner,direct_alice,direct_bob,direct_owner)
    with direct_vm.prank(direct_alice): c.revoke_certificate("CAL-2026-017")
    with direct_vm.expect_revert("CERTIFICATE_NO_LONGER_VALID"):
        c.consume_authorization(state["authorization_id"])

def test_same_wallet_cannot_supply_both_evidence_roles(direct_deploy,direct_vm,direct_owner,direct_alice):
    c=direct_deploy("contracts/calscope.py")
    c.set_calibrator(addr(direct_alice),"calibrator/certificates",True)
    c.set_facility("north-lab",addr(direct_alice),"facility/requirements",True)
    with direct_vm.prank(direct_alice):
        c.issue_certificate("CAL-2026-017","BAL-17",CERT_URL,sha(CERT),len(CERT.encode()))
        c.seal_requirement("north-lab","JOB-204",addr(direct_owner),"BAL-17",REQ_URL,sha(REQ),len(REQ.encode()))
    with direct_vm.expect_revert("EVIDENCE_AUTHORITIES_NOT_INDEPENDENT"):
        c.assess(addr(direct_alice),"CAL-2026-017","north-lab","JOB-204")

def test_authority_rotation_invalidates_previously_sealed_evidence(direct_deploy,direct_vm,direct_owner,direct_alice,direct_bob):
    c=direct_deploy("contracts/calscope.py"); setup(c,direct_vm,direct_owner,direct_alice,direct_bob,direct_owner)
    c.set_calibrator(addr(direct_alice),"calibrator/new-certificates",True)
    with direct_vm.expect_revert("CALIBRATOR_AUTHORITY_CHANGED"):
        c.assess(addr(direct_alice),"CAL-2026-017","north-lab","JOB-204")

