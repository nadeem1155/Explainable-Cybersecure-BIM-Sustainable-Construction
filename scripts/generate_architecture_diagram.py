"""
Generates publication-quality process and architecture model diagram for the Explainable Cybersecure BIM Framework.
Saves to results/figures/fig6_framework_model_architecture.png.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import os

os.makedirs("results/figures", exist_ok=True)

fig, ax = plt.subplots(figsize=(16, 12), dpi=300)
ax.set_xlim(0, 100)
ax.set_ylim(0, 100)
ax.axis('off')

# Background canvas styling
fig.patch.set_facecolor('#f8fafc')
ax.set_facecolor('#f8fafc')

def draw_box(x, y, w, h, title, subtitle="", color="#ffffff", edge_color="#334155", title_color="#0f172a", lw=1.5, boxstyle="round,pad=0.3"):
    rect = patches.FancyBboxPatch(
        (x, y), w, h, boxstyle=boxstyle,
        facecolor=color, edgecolor=edge_color, linewidth=lw
    )
    ax.add_patch(rect)
    if title:
        ax.text(x + w/2, y + h - (1.6 if subtitle else h/2), title, ha='center', va='center',
                fontsize=9.5, fontweight='bold', color=title_color)
    if subtitle:
        ax.text(x + w/2, y + (h - 1.6)/2, subtitle, ha='center', va='center',
                fontsize=7.5, color="#475569", wrap=True)

def draw_arrow(x1, y1, x2, y2, color="#475569", lw=1.5, text=""):
    ax.annotate(
        "", xy=(x2, y2), xytext=(x1, y1),
        arrowprops=dict(arrowstyle="->", color=color, lw=lw, shrinkA=3, shrinkB=3)
    )
    if text:
        ax.text((x1 + x2)/2, (y1 + y2)/2 + 0.8, text, ha='center', va='center', fontsize=7, color="#0f172a", fontweight='bold')

# Header Title
ax.text(50, 97.5, "AN EXPLAINABLE MULTI-OBJECTIVE ML FRAMEWORK FOR CYBERSECURE BIM SOFTWARE DESIGN",
        ha='center', va='center', fontsize=14, fontweight='bold', color="#0f172a")
ax.text(50, 95.2, "End-to-End System Process Model: Ingestion, Zero-Trust Defense, Physics Engines, Evolutionary Search & XAI",
        ha='center', va='center', fontsize=9.5, color="#64748b", style='italic')

# ==============================================================================
# LAYER 1: MULTI-MODAL DATA INGESTION & PROVENANCE (Top)
# ==============================================================================
draw_box(3, 80, 94, 13, "LAYER 1: MULTI-MODAL INGESTION & PROVENANCE LAYER", "", color="#f1f5f9", edge_color="#cbd5e1", title_color="#1e293b")

draw_box(5, 81.5, 20, 9, "BIM Geometry Ingestion", "buildingSMART IFC4 & IFC 2x3\nIfcOpenShell Unit Normalizer\nPhysical Volume & Class Extraction", color="#ffffff", edge_color="#3b82f6")
draw_box(29, 81.5, 19, 9, "Environmental EPDs", "German ÖKOBAUDAT (EN 15804)\nCradle-to-Grave (A1-C4) GWP\nNon-Renewable Primary Energy", color="#ffffff", edge_color="#10b981")
draw_box(52, 81.5, 19, 9, "Construction Costs", "CPWD Schedule of Rates 2021\nBasic Rates, Labour & Materials\nRegional Cost Index Scaling", color="#ffffff", edge_color="#f59e0b")
draw_box(75, 81.5, 20, 9, "Cybersecurity Telemetry", "UNSW ToN_IoT (NetFlow v2)\nUNB CICIoT2023 Benchmark\n159k Flows | 10 Attack Classes", color="#ffffff", edge_color="#ef4444")

# Flow down arrows from Ingestion
draw_arrow(15, 81.5, 15, 75, color="#3b82f6")
draw_arrow(38.5, 81.5, 38.5, 75, color="#10b981")
draw_arrow(61.5, 81.5, 61.5, 75, color="#f59e0b")
draw_arrow(85, 81.5, 85, 52, color="#ef4444")

# ==============================================================================
# LAYER 2: ZERO-TRUST SECURITY PERIMETER & GATEWAY (Upper Middle Left)
# ==============================================================================
draw_box(3, 56, 68, 19, "LAYER 2: ZERO-TRUST GATEWAY & ACCESS ENFORCEMENT (NIST SP 800-207)", "", color="#f8fafc", edge_color="#94a3b8")

draw_box(5, 58, 18, 14.5, "1. Cryptographic Auth", "HMAC-SHA256 JWT Token\n15-Minute Strict TTL\nReplay Nonce Validation\nPayload Decryption (AES-256)", color="#e0f2fe", edge_color="#0284c7")
draw_box(25, 58, 18, 14.5, "2. Token-Bucket Rate Limiter", "Capacity: 60 tokens\nRefill: 1.0 token/sec\nPrevents API Flooding\nAnti-DoS Perimeter Defense", color="#fef3c7", edge_color="#d97706")
draw_box(45, 58, 24, 14.5, "3. Least-Privilege RBAC Matrix", "Role vs Action Access Control:\n- Structural Engineer (Modify)\n- Sustainability Auditor (Read)\n- Viewer (Read Only)\nHard Decoupling Gate", color="#fee2e2", edge_color="#dc2626")

# Rejection and Tamper branch
draw_box(45, 48, 24, 6, "Deterministic Hard Rejection", "HTTP 401 Unauthorized / 403 Forbidden\n(Decoupled from ML Classifiers)", color="#fecaca", edge_color="#b91c1c")
draw_arrow(57, 58, 57, 54, color="#b91c1c", text="Denied")

# Model Integrity Check Box
draw_box(5, 48, 38, 6, "Cryptographic Model Integrity Verification", "SHA-256 Merkle Baseline Check | 100% Tamper Detection Accuracy", color="#dcfce7", edge_color="#16a34a")
draw_arrow(15, 58, 15, 54, color="#16a34a")

# ==============================================================================
# LAYER 3: CORE MULTI-OBJECTIVE OPTIMIZATION & PHYSICS ENGINES (Lower Left)
# ==============================================================================
draw_box(3, 21, 68, 25, "LAYER 3: CONSTRAINED MULTI-OBJECTIVE EVOLUTIONARY SEARCH (NSGA-II)", "", color="#f1f5f9", edge_color="#cbd5e1")

# Sub-engines
draw_box(5, 23, 19, 14, "Embodied Carbon Engine (f1)", "EN 15804 Cradle-to-Grave\nModules A1-A3 Manufacturing\nModule A4 Transport Haulage\nModule B4 Replacement Cycles\nModule C Net Circular Credit", color="#ffffff", edge_color="#10b981")
draw_box(26, 23, 19, 14, "Lifecycle Cost Engine (f2)", "CPWD DSR 2021 Schedule\nInitial Capital (C_init)\n30-Yr Discounted Maint. (NPV)\nFinishes Replacement (Yr 15,25)\nSocial Discount Rate r = 4.0%", color="#ffffff", edge_color="#f59e0b")
draw_box(47, 23, 22, 14, "Structural Safety Engine (f3, g1)", "IS 456 / Eurocode 2 Mechanics\nFlexural Limit Mu <= Mu,lim\nShear Resistance Vu <= Vuc\nDeflection delta <= L/350\nDemand-to-Capacity Ratio <= 1.0", color="#ffffff", edge_color="#3b82f6")

draw_box(5, 39, 64, 5.5, "Genome Decision Vector x = [m_beam, m_col, m_wall, m_rebar, alpha_beam, alpha_col]",
         "Candidate Materials: Concrete (M25, M30, M35, GGBS 50%, FA 30%), Glulam Timber, Recycled EAF Steel, AAC Blocks",
         color="#eff6ff", edge_color="#2563eb")

# Arrow from RBAC Permitted to Optimization
draw_arrow(57, 48, 57, 44.5, color="#16a34a", text="Permitted")

# Optimization loop arrow
draw_box(3, 8, 68, 11, "Evolutionary Pareto Frontier Convergence",
         "NSGA-II: Tournament Selection -> Simulated Binary Crossover (SBX, prob=0.90) -> Polynomial Mutation (PM, prob=0.15)\nHypervolume = 0.4822 | 100% Feasibility Rate across 10 Repeated Runs | Runtime: 15.53s",
         color="#f8fafc", edge_color="#0284c7")
draw_arrow(37, 23, 37, 19, color="#0284c7")

# ==============================================================================
# LAYER 4: CYBERSECURITY ANALYTICS SUITE (Right Column)
# ==============================================================================
draw_box(74, 48, 23, 27, "LAYER 4: CYBERSECURITY ML SUITE", "", color="#f8fafc", edge_color="#94a3b8")

draw_box(76, 64, 19, 9, "Leakage-Free Preprocessor", "RobustScaler (Fit on Train Only)\nIdentifier De-identification\nStratified Multi-Class Split", color="#ffffff", edge_color="#64748b")
draw_box(76, 50, 19, 12, "Intrusion Detection Models", "Supervised Classifiers:\n- XGBoost (F1: 0.9898, Lat: 1.03us)\n- Random Forest (F1: 0.9910)\n- LightGBM (Macro-F1: 0.7852)\nAnomaly: Isolation Forest", color="#ffffff", edge_color="#ef4444")

draw_arrow(85, 64, 85, 62, color="#ef4444")

# ==============================================================================
# LAYER 5: EXPLAINABLE AI & SYNTHESIS LAYER (Bottom Right)
# ==============================================================================
draw_box(74, 8, 23, 38, "LAYER 5: EXPLAINABLE AI (XAI)", "", color="#f8fafc", edge_color="#94a3b8")

draw_box(76, 33, 19, 11, "TreeSHAP Attribution Engine", "Global Feature Importance:\n1. LONGEST_FLOW_PKT\n2. L4_DST_PORT\n3. L7_PROTO\n4. TCP_WIN_MAX_IN\nLocal Flow Waterfalls", color="#ffffff", edge_color="#8b5cf6")
draw_box(76, 21, 19, 10, "Stability Auditing", "Rank-Biased Overlap (RBO)\nEvaluated across 5-Folds\nRBO = 0.9166 +/- 0.024\nConfirms Hypothesis H4", color="#ffffff", edge_color="#8b5cf6")
draw_box(76, 9.5, 19, 10, "Design Trade-Off Explainer", "Explains 3 Alternatives:\n- Carbon-Oriented (Timber/EAF)\n- Cost-Oriented (M25/Fly Ash)\n- Balanced (GGBS Concrete)", color="#ffffff", edge_color="#10b981")

draw_arrow(85, 50, 85, 44, color="#8b5cf6")
draw_arrow(85, 33, 85, 31, color="#8b5cf6")
draw_arrow(71, 13.5, 76, 13.5, color="#10b981", text="Pareto Front")

plt.tight_layout()
plt.savefig("results/figures/fig6_framework_model_architecture.png", bbox_inches='tight')
plt.close()
print("Saved results/figures/fig6_framework_model_architecture.png successfully!")
