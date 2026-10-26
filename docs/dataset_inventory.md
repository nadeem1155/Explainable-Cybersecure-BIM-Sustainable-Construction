# Dataset Inventory and Data Provenance

This document establishes the audit trail, acquisition provenance, technical schemas, and governance rules for all datasets utilized in the project:
**"An Explainable Multi-Objective Machine Learning Framework for Cybersecure BIM Software Design and Sustainable Smart Construction"**.

---

## 1. Primary Cybersecurity Dataset: ToN_IoT (NetFlow v2)

- **Official Source**: Cyber Range Lab, UNSW Canberra (https://research.unsw.edu.au/projects/toniot-datasets)
- **Harmonized Benchmark Representation**: NetFlow v2 format (Sarhan et al., University of Queensland / UNSW Canberra)
- **Storage Location**: `data/raw/ton_iot/ton_iot_network.csv`
- **Acquisition Timestamp**: 2026-10-26T17:54:20Z
- **File Format**: Standard RFC 4180 CSV, UTF-8 encoded
- **Total Record Count**: 159,289 network flow records
- **Feature Dimension**: 45 columns (43 predictive features, `Label` [binary], `Attack` [multi-class])
- **File Size**: 24,999,961 bytes (~24.99 MB)
- **SHA-256 Checksum**: `16d6efb5a03abdbca3a08c37613e478cf0a464effe2f338d6c87099134708e3f`
- **Class Breakdown**:
  - `Benign`: 57,384 flows (36.03%)
  - `scanning`: 35,785 flows (22.47%)
  - `xss`: 22,930 flows (14.40%)
  - `ddos`: 18,944 flows (11.89%)
  - `password`: 10,888 flows (6.84%)
  - `dos`: 6,713 flows (4.21%)
  - `injection`: 6,343 flows (3.98%)
  - `backdoor`: 194 flows (0.12%)
  - `mitm`: 73 flows (0.05%)
  - `ransomware`: 35 flows (0.02%)
  - **Binary Split**: Attack (`1`) = 101,905 flows (63.97%); Benign (`0`) = 57,384 flows (36.03%)
- **Data Governance & License**: Creative Commons Attribution 4.0 International (CC BY 4.0).

---

## 2. Independent IoT Cybersecurity Benchmark: CICIoT2023

- **Official Source**: Canadian Institute for Cybersecurity (CIC), University of New Brunswick (https://www.unb.ca/cic/datasets/iotdataset-2023.html)
- **Storage Location**: `data/raw/ciciot2023/ciciot2023_benchmark.csv`
- **Acquisition Timestamp**: 2026-10-26T17:54:20Z
- **File Format**: Standard CSV, UTF-8 encoded
- **Total Record Count**: 50,000 traffic window records (stratified balanced sample of 10,000 per class across 5 representative IoT traffic profiles)
- **Feature Dimension**: 40 columns (39 numerical traffic window features, `label`)
- **File Size**: 10,308,533 bytes (~10.31 MB)
- **SHA-256 Checksum**: `76fbf1510255b9385095b7f0853db2a49012d24e1519d2be60382d197b32b9df`
- **Class Breakdown**:
  - `Benign`: 10,000 samples (20.0%)
  - `DDoS-ICMP_Flood`: 10,000 samples (20.0%)
  - `DDoS-UDP_Flood`: 10,000 samples (20.0%)
  - `DDoS-TCP_Flood`: 10,000 samples (20.0%)
  - `DDoS-SYN_Flood`: 10,000 samples (20.0%)
- **Methodological Isolation Note**: CICIoT2023 is maintained strictly as an independent IoT benchmark. As required by Section 4.2 of the specification, its feature schema (sliding statistical window metrics) is fundamentally incompatible with NetFlow flow records. We report independent models and evaluate cross-domain divergence rather than fabricating an artificial common table.
- **License**: Free for academic and research purposes with attribution.

---

## 3. BIM Architectural & Structural Models: buildingSMART

- **Official Source**: buildingSMART International Certification Repository (https://github.com/buildingSMART/Certification-datasets)
- **Storage Location**: `data/raw/bim/`
- **Schema Standards**: IFC4 ADD2 TC1 (`ISO 16739-1:2018`) and IFC 2x3 TC1 (`ISO 16739:2005`)
- **Included Models**:
  1. `Building-Structural.ifc` (IFC4, 185,185 bytes, SHA-256: `903b5a005901...`): Contains `IfcBeam` (6), `IfcWall` (4), `IfcBuildingElementProxy` (2), `IfcFooting` (1), `IfcRoof` (1), `IfcChimney` (1), `IfcDiscreteAccessory` (2).
  2. `Building-Architecture.ifc` (IFC4, 142,325 bytes, SHA-256: `8790a1e193e8...`): Contains `IfcWall` (4), `IfcSlab` (3), `IfcBuildingElementProxy` (3), `IfcSpace` (2), `IfcFurniture` (1), `IfcRoof` (1).
  3. `Building-Hvac.ifc` (IFC4, 111,375 bytes, SHA-256: `2c17ecad2b0f...`): MEP distribution system.
  4. `Building-Structural-2x3.ifc` (IFC 2x3, 109,012 bytes, SHA-256: `25c09f1ea35dbf51e88b8829c423b9ce13a8264e69c620e932859772937aa25b`).
  5. `Building-Architecture-2x3.ifc` (IFC 2x3, 92,542 bytes, SHA-256: `c4db65ba847f6b369a95d6c54fa11f4750cbe6d59f021934e8923d8d578e5885`).
- **License**: Creative Commons Attribution 4.0 International (CC BY 4.0).

---

## 4. Environmental Life Cycle Assessment Database: ÖKOBAUDAT

- **Official Source**: Federal Ministry for Housing, Urban Development and Building (BMWSB) / BBSR Germany (https://www.oekobaudat.de)
- **Compliance Standard**: EN 15804 + A2, ISO 14040/44, ISO 21930
- **Storage Location**: `data/raw/oekobaudat/oekobaudat_factors.csv`
- **Assessment Scope**: Cradle-to-Gate (Modules A1–A3: raw material extraction, transport to factory, and manufacturing)
- **Total Materials Cataloged**: 15 standard construction materials spanning structural concrete grades (M20, M25, M30, M35, GGBS/Fly Ash low-carbon mixes), structural & reinforcing steel (virgin blast-furnace vs. recycled EAF), masonry units (burnt clay, fly-ash, AAC blocks), timber (glulam), glazing, and insulation.
- **Key Indicators**: Global Warming Potential (GWP in kg CO2 eq / unit), Primary Energy Non-Renewable (PENRT in MJ / unit).
- **Geographic Limitation & Harmonization**: Values represent the European/German industrial baseline. Geographic adaptation and sensitivity boundaries are explicitly formulated in Section 10 of the methodology.

---

## 5. Construction Schedule of Rates: CPWD (DSR 2021)

- **Official Source**: Central Public Works Department (CPWD), Ministry of Housing and Urban Affairs, Government of India (https://cpwd.gov.in)
- **Publication**: Delhi Schedule of Rates (DSR 2021), Volume 1 & 2
- **Storage Location**: `data/raw/cpwd/cpwd_dsr_2021.csv`
- **Baseline Year & Index**: Base Year 2021 (Cost Index = 100.0)
- **Scope & Sub-heads**:
  - Sub-head 04: Concrete Work
  - Sub-head 05: Reinforced Cement Concrete (RCC) & TMT Steel Reinforcement (Fe-500D)
  - Sub-head 06: Brick Work & Autoclaved Aerated Concrete (AAC) Masonry
  - Sub-head 10: Structural Steel Work
  - Sub-head 11: Flooring
  - Sub-head 12: Roofing and Glazing
- **Cost Formulation**: All unit rates are decomposed into Basic Rate, Material Component, and Labour Component in Indian Rupees (INR) per standard physical unit ($m^3$, $m^2$, tonne).

---

## 6. Controlled BIM Application Security Event Testbed

- **Source**: Secure BIM Zero-Trust Prototype Test Harness (Internal Application Generator)
- **Storage Location**: `data/synthetic/bim_security_events.csv`
- **Generation Method**: Controlled execution of 1,250 API requests against the FastAPI Zero-Trust server simulating 12 threat scenarios (e.g., token expiration, replay, role privilege escalation, unauthorized IFC geometry mutation, model hash integrity violation).
- **Mandatory Scientific Integrity Label**: Explicitly labeled as simulated testbed events. Never conflated with public telemetry or real-world operational attacks.
