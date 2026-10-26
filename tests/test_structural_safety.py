"""
Unit tests for Structural Mechanics and Limit State Safety Engine.
"""

import pytest
import pandas as pd
from src.structural_constraints.safety_engine import StructuralSafetyEngine

def test_beam_safety_mechanics():
    engine = StructuralSafetyEngine()
    beam = {
        "ifc_class": "IfcBeam",
        "length_m": 5.8,
        "width_m": 0.3,
        "height_m": 0.5,
        "density_kg_m3": 2400.0,
        "oekobaudat_id": "MAT_CONC_M25"
    }
    res = engine.evaluate_beam_safety(beam)
    assert "dcr_moment" in res
    assert "dcr_shear" in res
    assert "dcr_deflection" in res
    # With a 300x500 section over 5.8m span, the beam should be safely within limits (DCR < 1.0)
    assert res["dcr_max"] < 1.0
    assert res["is_safe"] is True
    assert res["constraint_violation"] == 0.0

def test_column_safety_mechanics():
    engine = StructuralSafetyEngine()
    col = {
        "ifc_class": "IfcColumn",
        "length_m": 0.4,
        "width_m": 0.4,
        "height_m": 3.5,
        "density_kg_m3": 2400.0,
        "oekobaudat_id": "MAT_CONC_M30"
    }
    res = engine.evaluate_column_safety(col)
    assert res["dcr_max"] < 1.0
    assert res["is_safe"] is True
    assert res["constraint_violation"] == 0.0

def test_underdesigned_element_detects_violation():
    engine = StructuralSafetyEngine()
    # Slender weak beam (150mm wide, 200mm deep over 8.0 meter span)
    slender_beam = {
        "ifc_class": "IfcBeam",
        "length_m": 8.0,
        "width_m": 0.15,
        "height_m": 0.20,
        "density_kg_m3": 2400.0,
        "oekobaudat_id": "MAT_CONC_M20"
    }
    res = engine.evaluate_beam_safety(slender_beam)
    # Deflection and moment must fail (DCR > 1.0)
    assert res["dcr_max"] > 1.0
    assert res["is_safe"] is False
    assert res["constraint_violation"] > 0.0
