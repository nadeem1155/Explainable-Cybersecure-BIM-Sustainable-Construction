"""
Unit tests for Embodied Carbon (LCA) and Life Cycle Costing (LCC) calculations.
"""

import pytest
import pandas as pd
from src.sustainability.carbon_calculator import CarbonCalculator
from src.lifecycle_cost.lcc_calculator import LifeCycleCostCalculator

@pytest.fixture
def sample_element():
    return {
        "guid": "TEST_BEAM_001",
        "ifc_class": "IfcBeam",
        "volume_m3": 1.2,
        "area_m2": 4.8,
        "length_m": 6.0,
        "density_kg_m3": 2400.0,
        "GWP_A1_A3_kgCO2eq": 245.0,
        "oeko_unit": "m3",
        "basic_rate_inr": 8450.0,
        "material_component_inr": 6400.0,
        "labour_component_inr": 2050.0,
        "cpwd_unit": "m3"
    }

def test_element_carbon_calculation(sample_element):
    calc = CarbonCalculator(transport_distance_km=50.0)
    res = calc.calculate_element_carbon(sample_element)
    
    # 1.2 m3 * 245 kg CO2/m3 = 294.0 kg CO2 (A1-A3)
    assert res["a1_a3_manufacturing"] == 294.0
    # Mass = 1.2 * 2.4 = 2.88 tonnes
    assert res["mass_tonnes"] == 2.88
    # A4 transport > 0
    assert res["a4_transport"] > 0
    # Total embodied carbon is positive
    assert res["total_embodied_carbon_kgCO2eq"] > 250.0

def test_element_cost_calculation(sample_element):
    lcc = LifeCycleCostCalculator(discount_rate=0.04, cost_index_multiplier=1.0)
    cost = lcc.calculate_element_initial_cost(sample_element)
    
    # 1.2 m3 * 8450 = 10,140 INR
    assert cost["initial_cost_inr"] == 10140.0
    assert cost["initial_material_inr"] == 7680.0
    assert cost["initial_labour_inr"] == 2460.0
    assert cost["initial_material_inr"] + cost["initial_labour_inr"] == cost["initial_cost_inr"]

def test_building_lcc_npv_discounting(sample_element):
    lcc = LifeCycleCostCalculator(assessment_years=30, discount_rate=0.04)
    df = pd.DataFrame([sample_element, sample_element])
    res = lcc.evaluate_building_lcc(df)
    
    summary = res["summary"]
    # Total initial cost = 2 * 10,140 * 1.05 = 21,294 INR
    assert summary["initial_capital_cost_inr"] > 20000.0
    assert summary["maintenance_npv_inr"] > 0.0
    assert summary["total_lifecycle_cost_npv_inr"] > summary["initial_capital_cost_inr"]
