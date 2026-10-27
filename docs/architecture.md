# System Architecture & Technical Specifications

## 1. High-Level Architectural Overview

The framework integrates three foundational pillars into a cohesive, testable, cloud-native architecture:
1. **Multi-Objective Sustainable Construction Optimization Engine**: Evolutionary multi-objective search (NSGA-II) balancing embodied carbon, lifecycle cost, and limit-state structural safety.
2. **Zero-Trust Cybersecure BIM Architecture**: Deterministic defense-in-depth security layer (NIST SP 800-207) enforcing authentication, least-privilege RBAC, cryptographic SHA-256 model integrity verification, and append-only audit logging.
3. **Cybersecurity Analytics & Explainable AI (XAI)**: Supervised intrusion detection (XGBoost, Random Forest, LightGBM) and TreeSHAP transparency explaining network threat detections and construction trade-offs.

![Framework Process Model Architecture](../results/figures/fig6_framework_model_architecture.png)
*Figure: Complete Multi-Tier Framework Process Model & System Architecture.*

```
+---------------------------------------------------------------------------------------------------------+
|                                    BIM CLIENTS & COLLABORATORS                                         |
|  Architects | Structural Engineers | Sustainability Auditors | BIM Managers | IoT Sensor Gateways        |
+---------------------------------------------------------------------------------------------------------+
                                                     |  HTTPS / TLS 1.3 (Bearer JWT)
                                                     v
+---------------------------------------------------------------------------------------------------------+
|                                  ZERO-TRUST SECURITY PERIMETER (API GATEWAY)                            |
|                                                                                                         |
|  +---------------------------+   +---------------------------+   +-----------------------------------+  |
|  |  Token Bucket Rate Limiter|   |   JWT Cryptographic Auth  |   |   RBAC / Least-Privilege Matrix   |  |
|  |  (Anti-DoS / Burst Limit) |   |   (HMAC-SHA256, Expiry)   |   |   (Role-Resource-Action Checks)   |  |
|  +---------------------------+   +---------------------------+   +-----------------------------------+  |
|                                                |                                                        |
|                                [Authorized Actions Only]                                                |
+---------------------------------------------------------------------------------------------------------+
                         |                                               |
                         v                                               v
+--------------------------------------------------+   +--------------------------------------------------+
|          PILLAR 1: BIM & SUSTAINABILITY          |   |          PILLAR 2: CYBERSECURITY ANALYTICS       |
|                                                  |   |                                                  |
|  +--------------------------------------------+  |   |  +--------------------------------------------+  |
|  |  IfcOpenShell Ingestion & Unit Normalizer  |  |   |  |  NetFlow v2 / Traffic Feature Extractor    |  |
|  |  (IFC 2x3 & IFC 4 Parsing, GUID Anchor)    |  |   |  |  (Leakage Prevention, Robust Scaling)      |  |
|  +--------------------------------------------+  |   |  +--------------------------------------------+  |
|                        |                         |   |                        |                         |
|                        v                         |   |                        v                         |
|  +--------------------------------------------+  |   |  +--------------------------------------------+  |
|  |  ÖKOBAUDAT EPD & CPWD DSR 2021 Mapper      |  |   |  |  Intrusion Detection Model Suite           |  |
|  |  (A1-C4 Embodied Carbon & 30-Yr LCC NPV)   |  |   |  |  (XGBoost, Random Forest, LightGBM, ISO)   |  |
|  +--------------------------------------------+  |   |  +--------------------------------------------+  |
|                        |                         |   |                        |                         |
|                        v                         |   |                        v                         |
|  +--------------------------------------------+  |   |  +--------------------------------------------+  |
|  |  Structural Limit-State Engineering Checks |  |   |  |  Cryptographic Model Tamper Detection      |  |
|  |  (IS 456 / Eurocode 2 Bending, Shear, Defl)|  |   |  |  (SHA-256 Merkle Hash Baseline Divergence) |  |
|  +--------------------------------------------+  |   |  +--------------------------------------------+  |
|                        |                         |   +--------------------------------------------------+
|                        v                                                       |
|  +--------------------------------------------+                                |
|  |  Constrained Evolutionary NSGA-II Engine   |                                |
|  |  (Pareto Optimal Frontier Exploration)     |                                |
|  +--------------------------------------------+                                |
+--------------------------------------------------+                             |
                         |                                                       |
                         +---------------------------+---------------------------+
                                                     |
                                                     v
+---------------------------------------------------------------------------------------------------------+
|                                    PILLAR 3: EXPLAINABLE AI (XAI) LAYER                                 |
|                                                                                                         |
|  +-----------------------------------------+         +-----------------------------------------------+  |
|  |  TreeSHAP Global & Local Attributions   |         |  Multi-Objective Pareto Trade-Off Explainer   |  |
|  |  (Beeswarm Plots, Attack Feature Impact)|         |  (Carbon-Oriented vs Cost-Oriented vs Balance)|  |
|  +-----------------------------------------+         +-----------------------------------------------+  |
|                        |                                                     |                          |
|                        +---------------------------+-------------------------+                          |
|                                                    v                                                    |
|                                  STABILITY AUDITING: RANK-BIASED OVERLAP                                |
+---------------------------------------------------------------------------------------------------------+
                                                     |
                                                     v
+---------------------------------------------------------------------------------------------------------+
|                                  INTERACTIVE STREAMLIT DASHBOARD & REST API                             |
|  Real-Time Metrics | 3D Pareto Plots | Threat Feeds | Structural Safety Status | Traceability Badges    |
+---------------------------------------------------------------------------------------------------------+
```

---

## 2. Component Interface Specifications

### 2.1 Ingestion Interface (`src.ingestion.ifc_parser`)
- **Input**: Path to IFC file (`.ifc`, STEP Part 21 format).
- **Processing**: Traverses `IfcProduct` spatial hierarchies, filters non-physical spaces, extracts geometry and property sets, converts units (detecting millimeters and converting to meters), maps associated materials via `IfcRelAssociatesMaterial`.
- **Output**: Pandas DataFrame containing element GUIDs, classifications, volumes ($m^3$), lengths ($m$), cross-sectional areas ($m^2$), and assigned material names.

### 2.2 Material Mapping Interface (`src.ingestion.material_mapper`)
- **Input**: Parsed BIM element records.
- **Lookup Tables**:
  - `data/raw/oekobaudat/oekobaudat_factors.csv` (15 EN 15804 compliant materials).
  - `data/raw/cpwd/cpwd_dsr_2021.csv` (14 DSR 2021 schedule rate items).
- **Output**: Enriched records with GWP (kg CO2 eq/unit), density ($kg/m^3$), basic rate (INR), material/labour splits, match confidence score, and matching method.

### 2.3 Sustainability & Cost Engines (`src.sustainability`, `src.lifecycle_cost`)
- **Carbon Formulation**:
  $$f_1(x) = \sum_{i=1}^N \left( Q_i \cdot GWP_i^{A1-A3} + M_i \cdot d \cdot EF_{transp} + Q_i \cdot GWP_i^{A5} + Q_i \cdot GWP_i^{B4} + Q_i \cdot GWP_i^{C1-C4} \right)$$
- **Life Cycle Cost NPV Formulation**:
  $$f_2(x) = C_{init}(x) + \sum_{t=1}^T \frac{C_{maint}(t, x)}{(1 + r)^t} + \sum_{k} \frac{C_{repl}(t_k, x)}{(1 + r)^{t_k}} + \frac{C_{eol}(x)}{(1 + r)^T}$$
  where $r = 0.04$, $T = 30$ years.

### 2.4 Structural Safety Engine (`src.structural_constraints`)
- **Flexural Limit State**: $M_u^{demand} \le M_u^{capacity} = 0.138 f_{ck} b d^2$.
- **Shear Limit State**: $V_u^{demand} \le V_u^{capacity} = \tau_c b d$.
- **Serviceability Deflection**: $\delta = \frac{5 w L^4}{384 E_c I_g} \le \frac{L}{350}$.
- **Constraint Violation Penalty**: $f_3(x) = \sum_k \max(0, \text{DCR}_k - 1.0) \times 1000.0$.

### 2.5 Zero-Trust Security Engine (`src.security_controls`)
- **Token Verification**: Validates HMAC-SHA256 signature, expiry ($exp > now$), and replay ($nonce \notin seen\_nonces$).
- **Access Enforcement**: Matrix lookup $action \in ROLE\_PERMISSIONS[role]$. Hard rejection (HTTP 401/403) before any business or ML logic.
- **Model Integrity**: Computes SHA-256 digest of IFC model at rest. Mismatch raises `TAMPER_DETECTED` alarm and halts downstream operations.
- **Audit Logging**: Appends tamper-evident audit records to `data/synthetic/bim_security_events.csv`.
