"""
Unit tests for IFC Ingestion and Feature Extraction Pipeline.
"""

import os
import pytest
from src.ingestion.ifc_parser import IFCParser
from src.ingestion.material_mapper import MaterialMapper

def test_ifc_parsing_ifc4():
    path = "data/raw/bim/Building-Structural.ifc"
    assert os.path.exists(path), "Building-Structural.ifc must exist"
    parser = IFCParser(path)
    df = parser.parse_all_elements()
    assert len(df) > 0, "Parser must extract physical elements"
    assert "guid" in df.columns
    assert "ifc_class" in df.columns
    assert "volume_m3" in df.columns
    # Check unit normalization: lengths must be within realistic engineering ranges (< 50m)
    assert df["length_m"].max() < 50.0
    assert df["volume_m3"].sum() > 5.0

def test_ifc_parsing_ifc2x3():
    path = "data/raw/bim/Building-Structural-2x3.ifc"
    assert os.path.exists(path), "Building-Structural-2x3.ifc must exist"
    parser = IFCParser(path)
    df = parser.parse_all_elements()
    assert len(df) > 0
    assert parser.schema in ["IFC2X3", "IFC2X3_TC1"]

def test_model_hash_integrity():
    path = "data/raw/bim/Building-Structural.ifc"
    parser = IFCParser(path)
    h1 = parser.compute_model_hash()
    h2 = parser.compute_model_hash()
    assert h1 == h2, "Model hash must be deterministic"
    assert len(h1) == 64, "SHA-256 hash must be 64 hexadecimal characters"

def test_material_enrichment():
    parser = IFCParser("data/raw/bim/Building-Structural.ifc")
    raw_df = parser.parse_all_elements()
    mapper = MaterialMapper()
    enriched = mapper.enrich_bim_elements(raw_df)
    assert len(enriched) == len(raw_df)
    assert "GWP_A1_A3_kgCO2eq" in enriched.columns
    assert "basic_rate_inr" in enriched.columns
    assert "match_confidence" in enriched.columns
    assert (enriched["match_confidence"] >= 0.70).all()
