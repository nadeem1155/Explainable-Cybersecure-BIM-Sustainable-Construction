"""
Material Mapper Engine.
Links IFC elements to ÖKOBAUDAT Environmental Factors and CPWD Schedule of Rates.
Maintains exact and category matching with provenance and confidence tracking.
"""

import pandas as pd
from typing import Dict, Any, Tuple, Optional

class MaterialMapper:
    def __init__(self, oekobaudat_csv: str = "data/raw/oekobaudat/oekobaudat_factors.csv",
                 cpwd_csv: str = "data/raw/cpwd/cpwd_dsr_2021.csv"):
        self.oeko_df = pd.read_csv(oekobaudat_csv)
        self.cpwd_df = pd.read_csv(cpwd_csv)

    def map_element(self, ifc_class: str, extracted_mat: str) -> Dict[str, Any]:
        """
        Map IFC element and material to ÖKOBAUDAT factor and CPWD rate.
        Returns mapped IDs, carbon factor, unit cost, and match metadata.
        """
        mat_lower = str(extracted_mat).lower()
        elem_lower = str(ifc_class).lower()

        # Rule-based matching with explicit confidence
        if "wood" in mat_lower or "timber" in mat_lower or "spruce" in mat_lower:
            oeko_match = "MAT_TIMBER_GLULAM"
            cpwd_match = "CPWD_10.01" # Timber/Structural frame installation
            confidence = 0.90
            method = "Keyword Exact (Timber)"
        elif "sand-lime" in mat_lower or "brick" in mat_lower or elem_lower in ["ifcwall", "ifcwallstandardcase"]:
            if "fly ash" in mat_lower:
                oeko_match = "MAT_BRICK_FLYASH"
                cpwd_match = "CPWD_06.04"
                confidence = 0.95
                method = "Exact (Fly Ash Brick)"
            elif "aac" in mat_lower or "aerated" in mat_lower:
                oeko_match = "MAT_BLOCK_AAC"
                cpwd_match = "CPWD_06.15"
                confidence = 0.95
                method = "Exact (AAC Block)"
            else:
                oeko_match = "MAT_BRICK_CLAY"
                cpwd_match = "CPWD_06.01"
                confidence = 0.88
                method = "Category (Clay Masonry)"
        elif "steel" in mat_lower or "metal" in mat_lower or elem_lower in ["ifcdiscreteaccessory", "ifcmember"]:
            if "recycled" in mat_lower or "eaf" in mat_lower:
                oeko_match = "MAT_STEEL_RECYCLED"
                cpwd_match = "CPWD_05.23"
                confidence = 0.95
                method = "Exact (Recycled Steel)"
            else:
                oeko_match = "MAT_STEEL_STRUCT"
                cpwd_match = "CPWD_10.01"
                confidence = 0.90
                method = "Category (Structural Steel)"
        elif "glass" in mat_lower or "glazing" in mat_lower or elem_lower == "ifcwindow":
            oeko_match = "MAT_GLASS_DOUBLE"
            cpwd_match = "CPWD_12.01"
            confidence = 0.90
            method = "Exact (Double Glazing)"
        elif "insul" in mat_lower:
            oeko_match = "MAT_INSUL_MINERAL"
            cpwd_match = "CPWD_04.01"
            confidence = 0.85
            method = "Category (Insulation)"
        else:
            # Default concrete matching based on structural class
            if "ggbs" in mat_lower:
                oeko_match = "MAT_CONC_GGBS"
                cpwd_match = "CPWD_05.04"
                confidence = 0.95
                method = "Exact (GGBS Concrete)"
            elif "30" in mat_lower or elem_lower == "ifccolumn":
                oeko_match = "MAT_CONC_M30"
                cpwd_match = "CPWD_05.03"
                confidence = 0.85
                method = "Category (M30 Concrete)"
            elif "20" in mat_lower:
                oeko_match = "MAT_CONC_M20"
                cpwd_match = "CPWD_05.01"
                confidence = 0.85
                method = "Category (M20 Concrete)"
            else:
                oeko_match = "MAT_CONC_M25"
                cpwd_match = "CPWD_05.02"
                confidence = 0.80
                method = "Engineering Default (M25 Concrete)"

        # Retrieve records
        oeko_row = self.oeko_df[self.oeko_df["material_id"] == oeko_match].iloc[0]
        cpwd_row = self.cpwd_df[self.cpwd_df["item_code"] == cpwd_match].iloc[0]

        return {
            "oekobaudat_id": oeko_match,
            "material_name": oeko_row["material_name"],
            "GWP_A1_A3_kgCO2eq": float(oeko_row["GWP_A1_A3_kgCO2eq"]),
            "PENRT_MJ": float(oeko_row["PENRT_MJ"]),
            "density_kg_m3": float(oeko_row["density_kg_m3"]),
            "oeko_unit": oeko_row["unit"],
            "cpwd_code": cpwd_match,
            "cpwd_description": cpwd_row["description"],
            "basic_rate_inr": float(cpwd_row["basic_rate_inr"]),
            "labour_component_inr": float(cpwd_row["labour_component_inr"]),
            "material_component_inr": float(cpwd_row["material_component_inr"]),
            "cpwd_unit": cpwd_row["unit"],
            "match_confidence": confidence,
            "match_method": method
        }

    def enrich_bim_elements(self, bim_df: pd.DataFrame) -> pd.DataFrame:
        """Enrich BIM parsed elements DataFrame with environmental and cost attributes."""
        enriched_rows = []
        for _, row in bim_df.iterrows():
            mapping = self.map_element(row["ifc_class"], row["extracted_material"])
            enriched = {**row.to_dict(), **mapping}
            enriched_rows.append(enriched)
        return pd.DataFrame(enriched_rows)

if __name__ == "__main__":
    from ifc_parser import IFCParser
    parser = IFCParser("data/raw/bim/Building-Structural.ifc")
    raw_df = parser.parse_all_elements()
    mapper = MaterialMapper()
    enriched_df = mapper.enrich_bim_elements(raw_df)
    print("Enriched Elements Sample:")
    print(enriched_df[["guid", "ifc_class", "material_name", "GWP_A1_A3_kgCO2eq", "basic_rate_inr", "match_confidence"]].head())
