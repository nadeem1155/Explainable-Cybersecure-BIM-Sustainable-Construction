"""
FastAPI Backend API Server for Explainable Cybersecure BIM Framework.
Provides Zero-Trust Authentication, Model Parsing, Embodied Carbon / LCC Calculation,
Multi-Objective Optimization, Integrity Verification, and XAI Explanations.
"""

import os
import time
from fastapi import FastAPI, Header, HTTPException, Depends, status
from pydantic import BaseModel, Field
from typing import Dict, List, Any, Optional

from src.ingestion.ifc_parser import IFCParser
from src.ingestion.material_mapper import MaterialMapper
from src.sustainability.carbon_calculator import CarbonCalculator
from src.lifecycle_cost.lcc_calculator import LifeCycleCostCalculator
from src.structural_constraints.safety_engine import StructuralSafetyEngine
from src.optimization.multi_objective_engine import MultiObjectiveOptimizationEngine
from src.security_controls.zero_trust_engine import ZeroTrustEngine

app = FastAPI(
    title="Explainable Cybersecure BIM & Sustainable Construction API",
    version="1.0.0",
    description="Zero-Trust API for BIM Structural, Environmental, Cost, and Security Analytics."
)

zt_engine = ZeroTrustEngine()
mapper = MaterialMapper()
carbon_calc = CarbonCalculator()
lcc_calc = LifeCycleCostCalculator()
safety_engine = StructuralSafetyEngine()

# Pre-parse base model for instantaneous query serving
BASE_IFC_PATH = "data/raw/bim/Building-Structural.ifc"
if os.path.exists(BASE_IFC_PATH):
    base_parser = IFCParser(BASE_IFC_PATH)
    base_elements_df = base_parser.parse_all_elements()
    base_enriched_df = mapper.enrich_bim_elements(base_elements_df)
    zt_engine.register_model_baseline_hash("struct_v1", BASE_IFC_PATH)
else:
    base_enriched_df = None

class TokenRequest(BaseModel):
    username: str
    role: str = Field(..., description="Role: bim_manager, structural_engineer, sustainability_auditor, viewer")
    expires_minutes: int = 15

class ActionRequest(BaseModel):
    action: str = Field(..., description="e.g. model:read, element:update, export:ifc")
    resource_id: str
    scenario_label: Optional[str] = "api_request"

class OptimizationRequest(BaseModel):
    pop_size: int = 40
    generations: int = 25
    algorithm: str = "NSGA-II"

@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "service": "Explainable Cybersecure BIM API",
        "timestamp": time.time(),
        "model_loaded": base_enriched_df is not None
    }

@app.post("/api/auth/token")
def issue_token(req: TokenRequest):
    """Issue authenticated Zero-Trust JWT token with HMAC-SHA256 signature."""
    valid_roles = ["bim_manager", "structural_engineer", "sustainability_auditor", "viewer"]
    if req.role not in valid_roles:
        raise HTTPException(status_code=400, detail=f"Invalid role. Must be one of {valid_roles}")
    token = zt_engine.generate_token(req.username, req.role, req.expires_minutes)
    return {
        "access_token": token,
        "token_type": "Bearer",
        "role": req.role,
        "expires_in_minutes": req.expires_minutes
    }

@app.post("/api/security/authorize")
def authorize_action(req: ActionRequest, authorization: Optional[str] = Header(None)):
    """Evaluate Zero-Trust authorization and record to append-only audit log."""
    token = authorization.replace("Bearer ", "") if authorization else None
    allowed, status_code, log_entry = zt_engine.authorize_action(
        token, req.action, req.resource_id, scenario_label=req.scenario_label or "api_call"
    )
    if not allowed:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN if "ROLE" in status_code else status.HTTP_401_UNAUTHORIZED,
            detail={"status": status_code, "log": log_entry}
        )
    return {"authorized": True, "status": status_code, "log": log_entry}

@app.get("/api/bim/elements")
def get_bim_elements(authorization: Optional[str] = Header(None)):
    """Retrieve extracted BIM elements (requires 'element:read')."""
    token = authorization.replace("Bearer ", "") if authorization else None
    allowed, status_code, log_entry = zt_engine.authorize_action(token, "element:read", "BIM_MODEL_STRUCTURAL")
    if not allowed:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=status_code)
    return {
        "element_count": len(base_enriched_df),
        "elements": base_enriched_df[["guid", "name", "ifc_class", "material_name", "volume_m3", "GWP_A1_A3_kgCO2eq", "basic_rate_inr"]].to_dict(orient="records")
    }

@app.get("/api/sustainability/evaluate")
def evaluate_sustainability():
    """Evaluate embodied carbon and lifecycle cost of current model state."""
    c_res = carbon_calc.evaluate_building_carbon(base_enriched_df)
    l_res = lcc_calc.evaluate_building_lcc(base_enriched_df)
    s_res = safety_engine.evaluate_building_structural_safety(base_enriched_df)
    return {
        "embodied_carbon": c_res["summary"],
        "lifecycle_cost": l_res["summary"],
        "structural_safety": {
            "is_feasible": s_res["is_structurally_feasible"],
            "max_dcr": s_res["max_demand_capacity_ratio"],
            "feasibility_rate": s_res["feasibility_rate_percent"]
        }
    }

@app.post("/api/optimization/run")
def run_optimization(req: OptimizationRequest, authorization: Optional[str] = Header(None)):
    """Run constrained evolutionary multi-objective optimization (requires 'element:update')."""
    token = authorization.replace("Bearer ", "") if authorization else None
    allowed, status_code, log_entry = zt_engine.authorize_action(token, "element:update", "BIM_OPTIMIZATION_ENGINE")
    if not allowed:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=status_code)

    opt = MultiObjectiveOptimizationEngine(base_enriched_df, random_seed=42)
    if req.algorithm.upper() == "NSGA-II":
        res = opt.run_nsga2(pop_size=req.pop_size, n_gen=req.generations)
    else:
        res = opt.run_weighted_sum_baseline(pop_size=req.pop_size, n_gen=req.generations)
    
    # Return serializable results
    if "pareto_front_f" in res:
        res["pareto_front_f"] = res["pareto_front_f"].tolist()
    if "pareto_front_x" in res:
        res["pareto_front_x"] = res["pareto_front_x"].tolist()

    return res

@app.get("/api/security/audit-logs")
def get_audit_logs(limit: int = 50, authorization: Optional[str] = Header(None)):
    """Retrieve latest security audit logs (requires 'security:audit_read')."""
    token = authorization.replace("Bearer ", "") if authorization else None
    allowed, status_code, log_entry = zt_engine.authorize_action(token, "security:audit_read", "SECURITY_LOGS")
    if not allowed:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=status_code)

    import pandas as pd
    if os.path.exists(zt_engine.audit_log_path):
        df = pd.read_csv(zt_engine.audit_log_path)
        return df.tail(limit).to_dict(orient="records")
    return []

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
