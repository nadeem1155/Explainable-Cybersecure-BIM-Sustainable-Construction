# BIM Zero-Trust Cybersecurity Threat Model & Security Architecture

## 1. Overview and Security Principles

Building Information Modeling (BIM) platforms are shifting from desktop-isolated CAD tools to distributed, cloud-native collaborative digital twins. This shift exposes sensitive infrastructure assets, architectural designs, HVAC control schemas, and structural topology to remote cyber threats.

Traditional perimeter-based security is insufficient for multi-stakeholder AEC collaboration where architects, general contractors, sub-contractors, MEP consultants, and structural engineers require dynamic access. This framework implements a **Zero-Trust Architecture (ZTA)** grounded in NIST SP 800-207 principles:
1. **Never Trust, Always Verify**: Every API interaction is treated as hostile regardless of whether it originates within or outside the network.
2. **Least Privilege Enforcement**: Access is granted strictly on a per-role and per-resource attribute basis (ABAC/RBAC).
3. **Cryptographic Integrity by Design**: Every BIM model revision is anchored by cryptographic SHA-256 state hashing and digital signatures.
4. **Decoupled Security Controls**: Hard authorization barriers are strictly separated from ML cybersecurity classifiers. Authorization rejection is deterministic and does not rely on ML inference.

---

## 2. STRIDE Threat Analysis for Cloud-Enabled BIM

| STRIDE Category | Threat Description in BIM Context | Attack Surface & Vector | Impact on AEC Project | Deterministic Prevention Mechanism | Active Detection Mechanism |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Spoofing** | Impersonation of authorized structural engineer or architect | Compromised JWT token, session hijacking, replay attack | Unauthorized project access, malicious design changes | Cryptographic JWT with RS256, short TTL (15 min), HMAC nonces, TLS 1.3 | Replay detection via redis/in-memory nonce store; rate anomaly monitoring |
| **Tampering** | Modifying IFC element properties, shifting beam axes, or swapping material specs | Insecure API update endpoint (`PUT /elements/{guid}`) | Structural failure, code violation, inflated carbon/cost | SHA-256 Merkle tree hashing of IFC entity states; digital signatures | Cryptographic hash divergence alarm; model integrity check upon checkout |
| **Repudiation** | Denying an unapproved material change or unauthorized export | Modifying logs or bypassing audit hooks | Legal dispute, untraceable structural defect | Append-only tamper-evident audit logging with cryptographic chaining | Continuous audit event pipeline tracking actor, IP, timestamp, action |
| **Information Disclosure** | Exfiltration of proprietary BIM geometry, HVAC security layouts, or tender costs | Unauthorized direct object reference (IDOR), API leaking IFC files | Loss of IP, exposure of physical security vulnerabilities in critical infrastructure | Fine-grained RBAC/ABAC at the IFC entity and model layer | Anomaly detection on bulk download requests; rate limiting |
| **Denial of Service** | Flooding BIM collaboration servers or parser service with malformed IFC files | High-volume API calls, XML/STEP entity expansion bombs | Project downtime, delayed site operations, worker standby costs | Token-bucket rate limiting (e.g., 60 req/min), request size caps (50 MB), strict schema validation | Network & host ML anomaly detection (ToN_IoT / CICIoT2023 models) |
| **Elevation of Privilege** | Subcontractor escalating permissions from `viewer` to `structural_engineer` | Parameter tampering, role manipulation in request payload | Unvetted modification of structural safety-critical elements | Server-side role resolution from cryptographically verified claims | Role-action policy verification matrix; security alert generation |

---

## 3. Threat Model Architecture and Decoupling Principle

```
+-----------------------------------------------------------------------------------+
|                            INCOMING CLIENT REQUEST                                |
+-----------------------------------------------------------------------------------+
                                         |
                                         v
+-----------------------------------------------------------------------------------+
|                     LAYER 1: DETERMINISTIC ZERO-TRUST GATEWAY                    |
|  - TLS 1.3 Transport Encryption                                                   |
|  - Token Signature & Expiration Validation (RS256 / HS256)                       |
|  - Rate Limiter (Token Bucket per IP/Actor)                                       |
|  - Input Validation & Schema Sanitation (Pydantic / Regex)                        |
|                                                                                   |
|  [Decision: Permitted or Hard Rejection 401/403/429]                              |
+-----------------------------------------------------------------------------------+
            | (If Permitted)                            | (If Denied / Suspicious)
            v                                           v
+------------------------------------------+  +-------------------------------------+
|  LAYER 2: RBAC & MODEL INTEGRITY CHECK   |  |   LAYER 4: CYBERSECURITY ANALYTICS  |
|  - Role vs Action Policy Engine          |  |   - Audit Event Logger              |
|  - IFC SHA-256 Hash Verification         |  |   - Feature Extraction Pipeline     |
|  - Tamper Detection                      |  |   - Supervised Intrusion Detection  |
+------------------------------------------+  |     (XGBoost / LightGBM / RF)       |
            |                                 |   - Isolation Forest Anomaly Engine |
            v                                 |   - SHAP Explainability Engine      |
+------------------------------------------+  +-------------------------------------+
|  LAYER 3: CORE BIM & SUSTAINABILITY APIS |                    |
|  - IFC Model Parser & Query Engine       |                    v
|  - Embodied Carbon & Cost Estimator      |      +---------------------------+
|  - Multi-Objective Optimization Engine   |      |  SECURITY DASHBOARD ALERT |
+------------------------------------------+      +---------------------------+
```

### The Decoupling Principle (Mandatory Rule from Section 8):
Under no circumstances is the deterministic authorization engine replaced by or subordinated to the ML cybersecurity classifier.
- If an actor lacks the `structural_engineer` role, the request is **rejected immediately**, even if the ML classifier predicts low anomaly probability (0.01).
- Conversely, if an actor is authorized but their request profile exhibits unusual patterns (e.g., unusual burst rates or abnormal payload sizes), the ML classifier flags a security alert for human audit without breaching access rules.
- Optimization algorithms are strictly prohibited from relaxing cybersecurity requirements to achieve lower carbon or lower cost.
