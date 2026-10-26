# Data Dictionary and Feature Specifications

This document defines the field schemas, data types, physical units, allowable ranges, and engineering semantics for each dataset across the three project pillars.

---

## 1. ToN_IoT Network Traffic Schema (NetFlow v2)

| Field Name | Data Type | Physical Unit | Description & Semantics |
| :--- | :--- | :--- | :--- |
| `IPV4_SRC_ADDR` | String | IPv4 address | Source IPv4 address of the flow initiator |
| `L4_SRC_PORT` | Integer | Port [0-65535] | Layer 4 source port |
| `IPV4_DST_ADDR` | String | IPv4 address | Destination IPv4 address |
| `L4_DST_PORT` | Integer | Port [0-65535] | Layer 4 destination port |
| `PROTOCOL` | Integer | Protocol ID | IP Protocol number (e.g., 6=TCP, 17=UDP, 1=ICMP) |
| `L7_PROTO` | Float | Protocol ID | Layer 7 application protocol identifier |
| `IN_BYTES` | Integer | Bytes | Inbound bytes transferred from source to destination |
| `IN_PKTS` | Integer | Packets | Number of inbound packets |
| `OUT_BYTES` | Integer | Bytes | Outbound bytes transferred from destination to source |
| `OUT_PKTS` | Integer | Packets | Number of outbound packets |
| `TCP_FLAGS` | Integer | Bitmask | Cumulative TCP flags observed in flow |
| `CLIENT_TCP_FLAGS` | Integer | Bitmask | TCP flags sent by client initiator |
| `SERVER_TCP_FLAGS` | Integer | Bitmask | TCP flags sent by responding server |
| `FLOW_DURATION_MILLISECONDS`| Integer | Milliseconds | Total flow active duration |
| `DURATION_IN` | Integer | Milliseconds | Duration of inbound stream |
| `DURATION_OUT` | Integer | Milliseconds | Duration of outbound stream |
| `MIN_TTL` | Integer | Hops [0-255] | Minimum Time to Live observed |
| `MAX_TTL` | Integer | Hops [0-255] | Maximum Time to Live observed |
| `LONGEST_FLOW_PKT` | Integer | Bytes | Largest packet size in flow |
| `SHORTEST_FLOW_PKT` | Integer | Bytes | Smallest packet size in flow |
| `MIN_IP_PKT_LEN` | Integer | Bytes | Minimum IP header packet length |
| `MAX_IP_PKT_LEN` | Integer | Bytes | Maximum IP header packet length |
| `SRC_TO_DST_SECOND_BYTES` | Float | Bytes/s | Transfer rate from source to destination |
| `DST_TO_SRC_SECOND_BYTES` | Float | Bytes/s | Transfer rate from destination to source |
| `RETRANSMITTED_IN_BYTES` | Integer | Bytes | Inbound retransmitted bytes (TCP loss/congestion) |
| `RETRANSMITTED_IN_PKTS` | Integer | Packets | Inbound retransmitted packet count |
| `RETRANSMITTED_OUT_BYTES` | Integer | Bytes | Outbound retransmitted bytes |
| `RETRANSMITTED_OUT_PKTS` | Integer | Packets | Outbound retransmitted packet count |
| `SRC_TO_DST_AVG_THROUGHPUT`| Integer | Bits/s | Average bit throughput from src to dst |
| `DST_TO_SRC_AVG_THROUGHPUT`| Integer | Bits/s | Average bit throughput from dst to src |
| `NUM_PKTS_UP_TO_128_BYTES` | Integer | Count | Frequency of packets sized <= 128 bytes |
| `NUM_PKTS_128_TO_256_BYTES`| Integer | Count | Frequency of packets sized 128-256 bytes |
| `NUM_PKTS_256_TO_512_BYTES`| Integer | Count | Frequency of packets sized 256-512 bytes |
| `NUM_PKTS_512_TO_1024_BYTES`|Integer | Count | Frequency of packets sized 512-1024 bytes |
| `NUM_PKTS_1024_TO_1514_BYTES`|Integer| Count | Frequency of packets sized 1024-1514 bytes |
| `TCP_WIN_MAX_IN` | Integer | Bytes | Maximum TCP receiver window size (inbound) |
| `TCP_WIN_MAX_OUT` | Integer | Bytes | Maximum TCP receiver window size (outbound) |
| `ICMP_TYPE` | Integer | Code | ICMP message type |
| `ICMP_IPV4_TYPE` | Integer | Code | ICMP IPv4 specific subtype |
| `DNS_QUERY_ID` | Integer | Identifier | DNS transaction query ID |
| `DNS_QUERY_TYPE` | Integer | Code | DNS query record type (A, AAAA, MX, etc.) |
| `DNS_TTL_ANSWER` | Integer | Seconds | Time to live of DNS response |
| `FTP_COMMAND_RET_CODE` | Integer | Status code | FTP command response code |
| `Label` | Integer | Binary {0, 1} | Binary classification target (0=Benign, 1=Malicious) |
| `Attack` | String | Categorical | Multi-class attack type: Benign, scanning, xss, ddos, password, dos, injection, backdoor, mitm, ransomware |

---

## 2. CICIoT2023 Benchmark Traffic Schema

| Field Name | Data Type | Physical Unit | Description & Semantics |
| :--- | :--- | :--- | :--- |
| `Header_Length` | Float | Bytes | Accumulated IP/transport header length |
| `Protocol Type` | Integer | Protocol ID | Transport protocol ID |
| `Time_To_Live` | Float | Hops | Average packet time to live |
| `Rate` | Float | Packets/s | Packet transmission rate in traffic window |
| `fin_flag_number` | Float | Ratio [0-1] | Fraction of packets containing FIN flag |
| `syn_flag_number` | Float | Ratio [0-1] | Fraction of packets containing SYN flag |
| `rst_flag_number` | Float | Ratio [0-1] | Fraction of packets containing RST flag |
| `psh_flag_number` | Float | Ratio [0-1] | Fraction of packets containing PSH flag |
| `ack_flag_number` | Float | Ratio [0-1] | Fraction of packets containing ACK flag |
| `ece_flag_number` | Float | Ratio [0-1] | Fraction of packets containing ECE flag |
| `cwr_flag_number` | Float | Ratio [0-1] | Fraction of packets containing CWR flag |
| `ack_count` | Integer | Count | Total ACK packets observed |
| `syn_count` | Integer | Count | Total SYN packets observed |
| `fin_count` | Integer | Count | Total FIN packets observed |
| `rst_count` | Integer | Count | Total RST packets observed |
| `HTTP`, `HTTPS`, `DNS`, `Telnet`, `SMTP`, `SSH`, `IRC`, `TCP`, `UDP`, `DHCP`, `ARP`, `ICMP`, `IGMP`, `IPv`, `LLC` | Float | Binary/Count | Protocol indicator flags |
| `Tot sum` | Float | Bytes | Total sum of packet sizes in sliding window |
| `Min`, `Max`, `AVG`, `Std` | Float | Bytes | Statistical dispersion of packet lengths |
| `Tot size` | Float | Bytes | Total aggregated size |
| `IAT` | Float | Seconds | Inter-Arrival Time between consecutive packets |
| `Number` | Integer | Count | Sample count in the active window |
| `Variance` | Float | $Bytes^2$ | Variance of packet sizes |
| `label` | String | Categorical | Attack class: Benign, DDoS-ICMP_Flood, DDoS-UDP_Flood, DDoS-TCP_Flood, DDoS-SYN_Flood |

---

## 3. ÖKOBAUDAT Environmental LCA Schema

| Field Name | Data Type | Physical Unit | Description |
| :--- | :--- | :--- | :--- |
| `material_id` | String | Unique Code | Material identifier (e.g., `MAT_CONC_M25`) |
| `material_name` | String | Text | Descriptive material and grade specification |
| `density_kg_m3` | Float | $kg/m^3$ | Standard material mass density |
| `unit` | String | Unit {$m^3$, tonne, $m^2$} | Declared physical unit in EPD |
| `GWP_A1_A3_kgCO2eq` | Float | $kg\ CO_2\ eq/unit$ | Global Warming Potential (Cradle-to-Gate Modules A1-A3) |
| `PENRT_MJ` | Float | $MJ/unit$ | Primary Energy Non-Renewable Total |
| `EPD_source` | String | Text | ÖKOBAUDAT dataset registration identifier |
| `standard` | String | Text | Compliance standard (EN 15804 / ISO 21930) |
| `geographic_scope` | String | Text | Territorial manufacturing baseline (DE / EU) |

---

## 4. CPWD Construction Schedule of Rates Schema

| Field Name | Data Type | Physical Unit | Description |
| :--- | :--- | :--- | :--- |
| `item_code` | String | Code (DSR) | Official CPWD item code (e.g., `CPWD_05.02`) |
| `sub_head` | String | Text | Classification chapter in DSR 2021 |
| `description` | String | Text | Technical specification, mixing, placing requirements |
| `unit` | String | Unit {$m^3$, tonne, $m^2$} | Standard measurement unit |
| `basic_rate_inr` | Float | INR / unit | Total all-inclusive schedule rate |
| `labour_component_inr` | Float | INR / unit | Direct labour and installation component |
| `material_component_inr`| Float | INR / unit | Direct material and consumables component |
| `cost_index_base` | Float | Index (Base 100) | Delhi Cost Index baseline reference |
| `effective_year` | Integer | Year | Edition year (2021) |

---

## 5. Controlled BIM Security Event Log Schema

| Field Name | Data Type | Semantics |
| :--- | :--- | :--- |
| `event_id` | String | Unique UUID v4 for the security audit event |
| `timestamp` | String | ISO 8601 UTC timestamp of request |
| `actor_id` | String | Authenticated subject identity (username or service account) |
| `actor_role` | String | RBAC role: `bim_manager`, `structural_engineer`, `sustainability_auditor`, `viewer`, `anonymous` |
| `resource_id` | String | Target BIM model or element GUID |
| `action` | String | Verb: `model:read`, `model:create`, `element:update`, `element:delete`, `export:ifc`, `admin:token_refresh` |
| `auth_outcome` | String | Decision: `PERMITTED`, `DENIED_FORBIDDEN`, `DENIED_UNAUTHENTICATED`, `DENIED_TOKEN_EXPIRED` |
| `integrity_status`| String | SHA-256 cryptographic check: `VERIFIED`, `TAMPER_DETECTED`, `NOT_APPLICABLE` |
| `request_ip` | String | Originating IP address |
| `anomaly_score` | Float | ML Zero-Trust cybersecurity anomaly score [0.0 - 1.0] |
| `scenario_label` | String | Explicit testbed label (e.g., `unauthorized_geometry_mutation`, `valid_auditor_read`) |
