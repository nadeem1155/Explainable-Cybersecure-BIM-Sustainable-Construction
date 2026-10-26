"""
Unit tests for Zero-Trust Security Controls, Token Verification, RBAC, and Tamper Detection.
"""

import os
import pytest
from src.security_controls.zero_trust_engine import ZeroTrustEngine

@pytest.fixture
def zt():
    test_log = "data/synthetic/test_security_audit.csv"
    if os.path.exists(test_log):
        os.remove(test_log)
    return ZeroTrustEngine(audit_log_path=test_log)

def test_token_issuance_and_verification(zt):
    token = zt.generate_token("engineer_priya", "structural_engineer", expires_delta_minutes=15)
    valid, msg, payload = zt.verify_token(token)
    assert valid is True
    assert msg == "TOKEN_VALID"
    assert payload["sub"] == "engineer_priya"
    assert payload["role"] == "structural_engineer"

def test_token_tampering_rejected(zt):
    token = zt.generate_token("engineer_priya", "structural_engineer", expires_delta_minutes=15)
    tampered = token[:-4] + "ABCD"
    valid, msg, payload = zt.verify_token(tampered)
    assert valid is False
    assert msg == "INVALID_SIGNATURE"

def test_token_expiration(zt):
    # Expired token (-5 minutes)
    token = zt.generate_token("expired_actor", "viewer", expires_delta_minutes=-5)
    valid, msg, payload = zt.verify_token(token)
    assert valid is False
    assert msg == "TOKEN_EXPIRED"

def test_replay_attack_detection(zt):
    token = zt.generate_token("replay_actor", "viewer", expires_delta_minutes=15)
    # First verification passes
    v1, msg1, _ = zt.verify_token(token)
    assert v1 is True
    # Replay of exact same token with identical nonce must be rejected
    v2, msg2, _ = zt.verify_token(token)
    assert v2 is False
    assert msg2 == "REPLAY_DETECTED"

def test_rbac_least_privilege_enforcement(zt):
    viewer_token = zt.generate_token("viewer_bob", "viewer")
    eng_token = zt.generate_token("engineer_alice", "structural_engineer")

    # Viewer cannot perform element:update
    ok, status, _ = zt.authorize_action(viewer_token, "element:update", "IfcBeam_101")
    assert ok is False
    assert status == "DENIED_ROLE_PRIVILEGE_VIOLATION"

    # Structural engineer can perform element:update
    ok2, status2, _ = zt.authorize_action(eng_token, "element:update", "IfcBeam_101")
    assert ok2 is True
    assert status2 == "PERMITTED"

def test_model_hash_tamper_detection(zt, tmp_path):
    # Create temporary IFC file
    model_file = tmp_path / "test_model.ifc"
    model_file.write_text("ISO-10303-21; ORIGINAL CONTENT;")
    
    # Register baseline
    zt.register_model_baseline_hash("m1", str(model_file))
    
    # Check untampered file
    ok, msg = zt.verify_model_integrity("m1", str(model_file), "actor1")
    assert ok is True
    assert msg == "VERIFIED"

    # Simulate 1-byte unauthorized modification
    model_file.write_text("ISO-10303-21; TAMPERED CONTENT;")
    ok_tamper, msg_tamper = zt.verify_model_integrity("m1", str(model_file), "actor1")
    assert ok_tamper is False
    assert msg_tamper == "TAMPER_DETECTED"
