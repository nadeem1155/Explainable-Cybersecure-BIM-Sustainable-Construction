# Data Licensing, Provenance, and Ethical Compliance

This document records the legal status, licenses, attribution statements, and terms of use for all data sources integrated into the project.

---

## 1. ToN_IoT Dataset
- **Ownership**: Cyber Range Lab, School of Engineering and Information Technology (SEIT), UNSW Canberra at the Australian Defence Force Academy (ADFA).
- **Authors**: Nour Moustafa et al.
- **License**: Creative Commons Attribution 4.0 International (CC BY 4.0).
- **Attribution Statement**: "The authors acknowledge the Cyber Range Lab of UNSW Canberra for making the ToN_IoT datasets publicly available for cybersecurity research."
- **Usage Compliance**: Used exclusively for academic training and benchmarking of machine learning classifiers. No PII is contained; IP addresses originate from a controlled closed cyber-range testbed.

---

## 2. CICIoT2023 Dataset
- **Ownership**: Canadian Institute for Cybersecurity (CIC), University of New Brunswick (UNB), Fredericton, Canada.
- **Authors**: E. C. P. Neto, S. Dadkhah, R. Ferreira, A. Zohourian, R. Lu, A. A. Ghorbani.
- **License**: Open Academic Research License (UNB CIC). Free for non-commercial educational and research use with mandatory citation.
- **Attribution Statement**: "Neto, E.C.P., et al., 'CICIoT2023: A Real-Time Dataset and Benchmark for Large-Scale Attacks in IoT Environments,' Sensors, 2023."
- **Usage Compliance**: Kept strictly as an independent IoT benchmark. In compliance with Section 4.2 of the specification, no cross-contamination or synthetic merging is conducted.

---

## 3. buildingSMART International Certification Models
- **Ownership**: buildingSMART International Ltd.
- **License**: Creative Commons Attribution 4.0 International (CC BY 4.0).
- **Attribution Statement**: "BIM datasets sourced from the official buildingSMART International Certification repository (https://github.com/buildingSMART/Certification-datasets)."
- **Usage Compliance**: Used solely for verifying parser compliance, extracting topological geometry, and verifying IFC 2x3 and IFC 4 schema adherence.

---

## 4. ÖKOBAUDAT Database
- **Ownership**: Federal Ministry for Housing, Urban Development and Building (BMWSB) and Federal Institute for Research on Building, Urban Affairs and Spatial Development (BBSR), Germany.
- **License**: Open Data / Free Use according to German Open Data Directive and Data License Germany (GeoBasis-DE / dl-de/by-2-0).
- **Attribution Statement**: "Life cycle assessment coefficients obtained from the official ÖKOBAUDAT database (https://www.oekobaudat.de), compliance verified against EN 15804."
- **Usage Compliance**: Environmental factors for structural materials are reported with explicit disclosure of geographic boundaries (EU/DE baseline).

---

## 5. Central Public Works Department (CPWD) Delhi Schedule of Rates
- **Ownership**: Central Public Works Department, Ministry of Housing and Urban Affairs, Government of India.
- **License**: Government Open Data / Public Domain for public engineering schedules and official rate analyses.
- **Attribution Statement**: "Construction unit costs referenced from the Central Public Works Department (CPWD) Delhi Schedule of Rates (DSR 2021), Government of India."
- **Usage Compliance**: Sourced rates serve as baseline unit costs. Local market indices and variability are exposed as configurable parameters in accordance with Section 4.6.

---

## 6. Simulated Controlled BIM Security Log Dataset
- **Origin**: Locally generated via automated test harness executing against the project's internal FastAPI Zero-Trust prototype.
- **Ethical & Safety Statement**: No live production networks, operational BIM servers, or third-party cloud infrastructure were probed, scanned, or attacked. All security events were produced strictly inside a sandboxed, isolated test harness running on localhost.
- **Mandatory Disclosure**: Explicitly documented as synthetic/simulated in all figures, tables, and manuscript sections.
