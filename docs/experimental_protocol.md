# Experimental Protocol: Formal Research Questions and Hypotheses

This protocol establishes the rigorous scientific methodology for evaluating the framework across six research questions (RQ1–RQ6) in accordance with Section 3 and Section 11 of the specification.

---

## Research Question 1 (RQ1): Sustainable Multi-Objective Optimization

**Question**: How effectively can evolutionary multi-objective optimization identify feasible construction alternatives that reduce embodied carbon and lifecycle cost while maintaining structural safety?

- **Hypothesis $H_1$**: Constrained evolutionary multi-objective optimization (NSGA-II) generates a set of non-dominated Pareto solutions that achieve at least a 15% reduction in embodied carbon (GWP A1-A3) and at least a 10% reduction in 30-year lifecycle cost compared to standard baseline concrete/brick construction specifications, while maintaining 100% compliance with structural safety constraints (unity check $\le 1.0$, deflection $\le L/350$).
- **Null Hypothesis $H_{1,0}$**: NSGA-II solutions do not achieve statistically significant reductions in both embodied carbon and lifecycle cost without violating structural feasibility constraints compared to standard baseline specifications.
- **Baseline**: Standard baseline construction design (M25 Conventional Concrete + Fe-500 Rebar + Burnt Clay Brick) evaluated under identical structural load requirements.
- **Alternative Optimizers**: Single-objective Weighted-Sum Genetic Algorithm, and Random Uniform Exploration.
- **Independent Variables**: Population size ($N=50, 100$), Generations ($G=50, 100$), Crossover probability ($p_c=0.9$), Mutation probability ($p_m=0.1$).
- **Dependent Variables**: Embodied carbon ($kg\ CO_2\ eq$), 30-year Net Present Value lifecycle cost ($INR$), structural demand-to-capacity ratio ($\sigma / \sigma_{allow}$), Hypervolume metric ($HV$), and feasibility rate (%).
- **Acceptance Criterion**: $H_1$ is accepted if NSGA-II produces Pareto solutions with $>15\%$ carbon reduction and $>10\%$ cost reduction with $100\%$ structural feasibility rate and significantly superior Hypervolume ($p < 0.05$ across 10 repeated stochastic runs).

---

## Research Question 2 (RQ2): Machine Learning Cybersecurity Analytics

**Question**: How effectively can machine learning identify attacks and abnormal behavior in heterogeneous network and IoT security datasets?

- **Hypothesis $H_2$**: Gradient-boosted decision trees (XGBoost, LightGBM) trained on NetFlow v2 features achieve Macro-F1 $\ge 0.90$ on multi-class intrusion detection across rare and frequent attack classes in the ToN_IoT dataset, outperforming linear baselines (Logistic Regression) and unsupervised anomaly detection (Isolation Forest).
- **Null Hypothesis $H_{2,0}$**: Gradient-boosted models do not achieve a statistically superior Macro-F1 compared to linear and unsupervised baselines on multi-class attack identification.
- **Baseline Models**: Logistic Regression (linear baseline), Random Forest (ensemble bagging baseline), Isolation Forest (unsupervised anomaly baseline).
- **Independent Variables**: Model architecture (Logistic Regression, Random Forest, LightGBM, XGBoost, Isolation Forest), feature scaling (RobustScaler), class weighting (balanced vs unweighted).
- **Dependent Variables**: Binary Precision, Recall, F1-Score, Multi-class Macro-F1, Multi-class Weighted-F1, False Positive Rate (FPR), ROC-AUC, PR-AUC, and inference latency per flow ($\mu s$).
- **Acceptance Criterion**: $H_2$ is accepted if XGBoost/LightGBM achieves Macro-F1 $\ge 0.90$ with FPR $\le 0.02$ on the holdout test set with statistically significant superiority over Logistic Regression ($p < 0.01$).

---

## Research Question 3 (RQ3): BIM Application Security Verification

**Question**: How effectively do the implemented Zero-Trust controls prevent unauthorized access, prohibited operations, and unauthorized BIM model modifications?

- **Hypothesis $H_3$**: The decoupled Zero-Trust authorization and cryptographic integrity verification engine achieves a 100% rejection rate for prohibited actions (unauthenticated, expired token, role privilege escalation) and 100% detection rate for model file tampering, with an API enforcement latency overhead of less than 20 milliseconds per request.
- **Null Hypothesis $H_{3,0}$**: The Zero-Trust enforcement engine allows false authorizations or fails to detect model tampering, or introduces an enforcement latency exceeding 20 ms.
- **Baseline**: Legacy perimeter model (no token expiration enforcement, permissive role boundaries, no cryptographic hashing).
- **Test Scenarios (12 Distinct Attack Vectors)**:
  1. Valid authorized read
  2. Missing authentication token
  3. Expired JWT token
  4. Invalid cryptographic signature
  5. Role escalation (viewer attempting element modification)
  6. Role escalation (sustainability auditor attempting structural delete)
  7. Unauthorized IFC model download
  8. Cryptographic hash tampering (1-byte modification of IFC file)
  9. Malformed API payload injection
  10. High-frequency API burst (Rate-limit breach)
  11. Replayed authentication attempt
  12. Valid authorized modification by structural engineer
- **Dependent Variables**: Unauthorized Action Rejection Rate (%), Tamper Detection Accuracy (%), Enforcement Latency ($ms$).
- **Acceptance Criterion**: $H_3$ is accepted if Rejection Rate = 100%, Tamper Detection = 100%, and mean enforcement latency $\le 20\ ms$.

---

## Research Question 4 (RQ4): Explainable AI Transparency

**Question**: Can SHAP-based explanations make machine learning predictions and multi-objective construction trade-offs transparent, interpretable, and auditable?

- **Hypothesis $H_4$**: TreeSHAP feature attributions identify a stable, consistent set of top-ranking predictive features across cybersecurity detections and sustainability regression models, with ranking stability ($RBO > 0.85$ across subsamples) that aligns with domain engineering principles.
- **Null Hypothesis $H_{4,0}$**: Feature attribution rankings are unstable or contradict verified engineering relationships.
- **Evaluation Procedure**: Compute global TreeSHAP summary plots, beeswarm distributions, local waterfall explanations for high-risk attacks and low-carbon design alternatives, and Rank-Biased Overlap (RBO) stability tests across five cross-validation folds.
- **Acceptance Criterion**: $H_4$ is accepted if top-5 feature attribution stability exhibits $RBO \ge 0.85$ and local explanations faithfully reflect ground-truth packet/engineering attributes.

---

## Research Question 5 (RQ5): Cybersecurity Generalization and Domain Transfer

**Question**: How does cybersecurity detection performance change when evaluated across separate datasets, capture environments, and attack categories?

- **Hypothesis $H_5$**: Cybersecurity models trained on one IoT environment (ToN_IoT) cannot be directly transferred to an independently collected IoT environment (CICIoT2023) without severe performance degradation due to fundamental feature schema divergence, validating the methodological requirement to evaluate independent benchmarks separately.
- **Evaluation Procedure**: Contrast the independent classification performance on ToN_IoT and CICIoT2023; attempt schema mapping between overlapping statistical attributes; measure cross-dataset transfer loss.
- **Acceptance Criterion**: $H_5$ is accepted if cross-domain feature mapping fails to maintain benchmark performance, providing experimental justification for independent evaluations.

---

## Research Question 6 (RQ6): Integrated Framework System Performance

**Question**: What trade-offs arise among sustainability, cost, safety, security-control overhead, model performance, and computational efficiency?

- **Hypothesis $H_6$**: The fully integrated framework delivers end-to-end multi-objective design optimization and real-time Zero-Trust cybersecurity monitoring with an aggregate system pipeline overhead of less than 1.5 seconds per design cycle, demonstrating operational feasibility for cloud-connected BIM workflows.
- **Ablation Configurations**:
  - Full Framework (Optimization + Zero-Trust + ML Intrusion Detection + SHAP)
  - Variant A: Without Evolutionary Optimization (Static Manual Specification)
  - Variant B: Without ML Cybersecurity Analytics (Rule-Only Logging)
  - Variant C: Without SHAP Explainability Layer
- **Dependent Variables**: End-to-end latency, CPU/memory utilization, carbon savings, cost savings, safety compliance, security audit completeness.
- **Acceptance Criterion**: Full framework retains all safety, security, and sustainability gains with total computational run-time $\le 1.5$ seconds per evaluation batch.
