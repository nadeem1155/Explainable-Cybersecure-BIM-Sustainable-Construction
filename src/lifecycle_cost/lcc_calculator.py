"""
Life Cycle Costing (LCC) Engine.
Computes Initial Capital Costs (CPWD DSR 2021) and Net Present Value (NPV)
over a 30-year assessment horizon considering maintenance, replacement, and end-of-life salvage.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any

class LifeCycleCostCalculator:
    def __init__(self, assessment_years: int = 30,
                 discount_rate: float = 0.04, # 4% real social discount rate
                 annual_maintenance_ratio: float = 0.015, # 1.5% of C_init per year
                 cost_index_multiplier: float = 1.05): # CPWD CI adjustment factor
        self.assessment_years = assessment_years
        self.discount_rate = discount_rate
        self.annual_maintenance_ratio = annual_maintenance_ratio
        self.cost_index = cost_index_multiplier

    def calculate_element_initial_cost(self, element: Dict[str, Any]) -> Dict[str, float]:
        """Calculate initial capital cost (Material + Labour) based on CPWD unit rates."""
        volume = float(element.get("volume_m3", 0.0))
        area = float(element.get("area_m2", 0.0))
        mass_tonnes = float(element.get("mass_tonnes", (volume * float(element.get("density_kg_m3", 2400.0))) / 1000.0))
        
        basic_rate = float(element.get("basic_rate_inr", 8450.0)) * self.cost_index
        labour_component = float(element.get("labour_component_inr", 2050.0)) * self.cost_index
        material_component = float(element.get("material_component_inr", 6400.0)) * self.cost_index
        unit = str(element.get("cpwd_unit", "m3")).lower()

        if "m3" in unit:
            qty = volume
        elif "tonne" in unit:
            qty = mass_tonnes
        elif "m2" in unit:
            qty = area
        else:
            qty = volume

        initial_cost = qty * basic_rate
        initial_labour = qty * labour_component
        initial_material = qty * material_component

        return {
            "initial_cost_inr": round(initial_cost, 2),
            "initial_material_inr": round(initial_material, 2),
            "initial_labour_inr": round(initial_labour, 2),
            "bill_quantity": round(qty, 3)
        }

    def evaluate_building_lcc(self, enriched_elements_df: pd.DataFrame) -> Dict[str, Any]:
        """
        Evaluate full lifecycle cost across all building elements.
        Computes Initial Capital Cost, Annual Discounted Maintenance,
        Periodic Replacement at Year 15 & 25, and End-of-Life Demolition/Salvage.
        """
        initial_total = 0.0
        material_total = 0.0
        labour_total = 0.0
        element_breakdowns = []

        for _, row in enriched_elements_df.iterrows():
            cost_dict = self.calculate_element_initial_cost(row.to_dict())
            initial_total += cost_dict["initial_cost_inr"]
            material_total += cost_dict["initial_material_inr"]
            labour_total += cost_dict["initial_labour_inr"]
            element_breakdowns.append({**row.to_dict(), **cost_dict})

        # Net Present Value Discounting:
        # 1. Maintenance NPV: Sum_{t=1}^T (C_maint / (1 + r)^t)
        # Uniform series present worth factor: P = A * [((1+r)^T - 1) / (r*(1+r)^T)]
        r = self.discount_rate
        T = self.assessment_years
        pwf_uniform = ((1.0 + r)**T - 1.0) / (r * (1.0 + r)**T)
        annual_maintenance = initial_total * self.annual_maintenance_ratio
        maintenance_npv = annual_maintenance * pwf_uniform

        # 2. Periodic Replacement at Year 15 and Year 25 (non-structural items like finishes/partitions ~10% of C_init)
        replacement_base = initial_total * 0.10
        repl_yr15_npv = replacement_base / ((1.0 + r)**15)
        repl_yr25_npv = replacement_base / ((1.0 + r)**25)
        total_replacement_npv = repl_yr15_npv + repl_yr25_npv

        # 3. End-of-Life Deconstruction & Residual Salvage at Year 30 (net ~3% of initial cost)
        eol_nominal = initial_total * 0.03
        eol_npv = eol_nominal / ((1.0 + r)**T)

        total_lifecycle_cost_npv = initial_total + maintenance_npv + total_replacement_npv + eol_npv

        summary = {
            "initial_capital_cost_inr": round(initial_total, 2),
            "material_component_inr": round(material_total, 2),
            "labour_component_inr": round(labour_total, 2),
            "annual_maintenance_inr": round(annual_maintenance, 2),
            "maintenance_npv_inr": round(maintenance_npv, 2),
            "replacement_npv_inr": round(total_replacement_npv, 2),
            "end_of_life_npv_inr": round(eol_npv, 2),
            "total_lifecycle_cost_npv_inr": round(total_lifecycle_cost_npv, 2),
            "discount_rate": r,
            "assessment_years": T
        }

        return {
            "summary": summary,
            "element_details": pd.DataFrame(element_breakdowns)
        }

if __name__ == "__main__":
    from src.ingestion.ifc_parser import IFCParser
    from src.ingestion.material_mapper import MaterialMapper
    
    parser = IFCParser("data/raw/bim/Building-Structural.ifc")
    raw_df = parser.parse_all_elements()
    mapper = MaterialMapper()
    enriched_df = mapper.enrich_bim_elements(raw_df)
    
    lcc_calc = LifeCycleCostCalculator()
    results = lcc_calc.evaluate_building_lcc(enriched_df)
    print("Lifecycle Cost Assessment Summary (Building-Structural.ifc):")
    for k, v in results["summary"].items():
        print(f"  {k}: {v}")
