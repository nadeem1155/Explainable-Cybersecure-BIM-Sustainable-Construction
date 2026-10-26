"""
Embodied Carbon and LCA Assessment Engine.
Calculates Cradle-to-Gate (A1-A3), Transport (A4), Replacement (B4), and End-of-Life (C1-C4)
carbon emissions for BIM elements based on EN 15804 / ÖKOBAUDAT indicators.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any

class CarbonCalculator:
    def __init__(self, transport_distance_km: float = 50.0,
                 freight_emission_factor_kgCO2_per_tkm: float = 0.095,
                 end_of_life_recycling_credit_ratio: float = 0.15):
        """
        transport_distance_km: Average delivery haulage distance in km
        freight_emission_factor_kgCO2_per_tkm: Heavy goods vehicle emissions (0.095 kg CO2/tonne-km)
        end_of_life_recycling_credit_ratio: Net benefit of circular steel/aggregates recovery
        """
        self.transport_distance_km = transport_distance_km
        self.freight_emission_factor = freight_emission_factor_kgCO2_per_tkm
        self.eol_credit_ratio = end_of_life_recycling_credit_ratio

    def calculate_element_carbon(self, element: Dict[str, Any]) -> Dict[str, float]:
        """Calculate carbon breakdown for a single BIM element."""
        volume = float(element.get("volume_m3", 0.0))
        area = float(element.get("area_m2", 0.0))
        density = float(element.get("density_kg_m3", 2400.0))
        gwp_factor = float(element.get("GWP_A1_A3_kgCO2eq", 245.0))
        unit = str(element.get("oeko_unit", "m3")).lower()

        # Calculate element mass in tonnes
        mass_tonnes = (volume * density) / 1000.0

        # Module A1-A3: Cradle-to-Gate Manufacturing
        if "m3" in unit:
            a1_a3 = volume * gwp_factor
        elif "tonne" in unit:
            a1_a3 = mass_tonnes * gwp_factor
        elif "m2" in unit:
            a1_a3 = area * gwp_factor
        else:
            a1_a3 = volume * gwp_factor

        # Module A4: Transportation to Site
        a4_transport = mass_tonnes * self.transport_distance_km * self.freight_emission_factor

        # Module A5: Construction Installation (estimated ~4% of A1-A3)
        a5_install = a1_a3 * 0.04

        # Module B4: Replacement across 30-year lifecycle (structural elements = 0, finishes/proxy = 1 cycle)
        ifc_class = str(element.get("ifc_class", "")).lower()
        if "wall" in ifc_class or "proxy" in ifc_class:
            b4_replacement = a1_a3 * 0.10 # partial maintenance/finishes
        else:
            b4_replacement = 0.0

        # Module C1-C4: Deconstruction & End-of-Life (demolition + disposal minus recycling credits)
        c_eol = (mass_tonnes * 15.0) - (a1_a3 * self.eol_credit_ratio) # 15 kg CO2/tonne deconstruction

        total_embodied = a1_a3 + a4_transport + a5_install + b4_replacement + c_eol

        return {
            "a1_a3_manufacturing": round(a1_a3, 2),
            "a4_transport": round(a4_transport, 2),
            "a5_construction": round(a5_install, 2),
            "b4_replacement": round(b4_replacement, 2),
            "c_end_of_life": round(c_eol, 2),
            "total_embodied_carbon_kgCO2eq": round(total_embodied, 2),
            "mass_tonnes": round(mass_tonnes, 3)
        }

    def evaluate_building_carbon(self, enriched_elements_df: pd.DataFrame) -> Dict[str, Any]:
        """Aggregate embodied carbon across all BIM elements in a building model."""
        totals = {
            "a1_a3_manufacturing": 0.0,
            "a4_transport": 0.0,
            "a5_construction": 0.0,
            "b4_replacement": 0.0,
            "c_end_of_life": 0.0,
            "total_embodied_carbon_kgCO2eq": 0.0,
            "mass_tonnes": 0.0
        }
        element_breakdowns = []
        for _, row in enriched_elements_df.iterrows():
            elem_carbon = self.calculate_element_carbon(row.to_dict())
            for k in totals:
                totals[k] += elem_carbon.get(k, 0.0)
            element_breakdowns.append({**row.to_dict(), **elem_carbon})

        for k in totals:
            totals[k] = round(totals[k], 2)
        totals["total_mass_tonnes"] = totals.pop("mass_tonnes")

        return {
            "summary": totals,
            "element_details": pd.DataFrame(element_breakdowns)
        }

if __name__ == "__main__":
    from src.ingestion.ifc_parser import IFCParser
    from src.ingestion.material_mapper import MaterialMapper
    
    parser = IFCParser("data/raw/bim/Building-Structural.ifc")
    raw_df = parser.parse_all_elements()
    mapper = MaterialMapper()
    enriched_df = mapper.enrich_bim_elements(raw_df)
    
    calculator = CarbonCalculator()
    results = calculator.evaluate_building_carbon(enriched_df)
    print("Carbon Assessment Summary (Building-Structural.ifc):")
    for k, v in results["summary"].items():
        print(f"  {k}: {v}")
