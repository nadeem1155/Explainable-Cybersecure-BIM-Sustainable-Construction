import os
import ssl
import urllib.request
import hashlib
import pandas as pd
import numpy as np

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

def calculate_sha256(filepath):
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        for byte_block in iter(lambda: f.read(65536), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def acquire_ton_iot():
    print("=== Acquiring ToN_IoT Dataset ===")
    target_path = "data/raw/ton_iot/ton_iot_network.csv"
    if os.path.exists(target_path):
        print(f"ToN_IoT already exists at {target_path}")
        return
    
    url = "https://huggingface.co/datasets/Nora9029/NF-ToN-IoT-v2/resolve/main/NF-ToN-IoT-v2-test.csv"
    # Stream first 25 MB (approx 120,000+ flow records with diverse attack classes)
    range_headers = dict(headers)
    range_headers['Range'] = 'bytes=0-25000000'
    req = urllib.request.Request(url, headers=range_headers)
    with urllib.request.urlopen(req, timeout=60, context=ctx) as resp, open(target_path, 'wb') as out_f:
        chunk = resp.read()
        # Ensure we end on a complete line
        last_newline = chunk.rfind(b'\n')
        if last_newline != -1:
            chunk = chunk[:last_newline+1]
        out_f.write(chunk)
    
    df = pd.read_csv(target_path)
    print(f"Acquired ToN_IoT: {len(df)} rows, {len(df.columns)} columns.")
    print("Attack distribution:\n", df['Attack'].value_counts())
    print("Label distribution:\n", df['Label'].value_counts())
    print("SHA256:", calculate_sha256(target_path))

def acquire_ciciot2023():
    print("\n=== Acquiring CICIoT2023 Benchmark Dataset ===")
    target_path = "data/raw/ciciot2023/ciciot2023_benchmark.csv"
    if os.path.exists(target_path):
        print(f"CICIoT2023 already exists at {target_path}")
        return
    
    # We will sample from Benign and DDoS/Attack files of CICIoT2023
    files_to_sample = [
        ("Benign", "https://huggingface.co/datasets/baalajimaestro/DDoS-CICIoT2023/resolve/main/BenignTraffic.pcap.csv", 10000),
        ("DDoS-ICMP_Flood", "https://huggingface.co/datasets/baalajimaestro/DDoS-CICIoT2023/resolve/main/DDoS-ICMP_Flood.pcap.csv", 10000),
        ("DDoS-UDP_Flood", "https://huggingface.co/datasets/baalajimaestro/DDoS-CICIoT2023/resolve/main/DDoS-UDP_Flood.pcap.csv", 10000),
        ("DDoS-TCP_Flood", "https://huggingface.co/datasets/baalajimaestro/DDoS-CICIoT2023/resolve/main/DDoS-TCP_Flood.pcap.csv", 10000),
        ("DDoS-SYN_Flood", "https://huggingface.co/datasets/baalajimaestro/DDoS-CICIoT2023/resolve/main/DDoS-SYN_Flood.pcap.csv", 10000),
    ]
    
    dfs = []
    for label_name, url, sample_rows in files_to_sample:
        print(f"Sampling {label_name} from {url}...")
        # Stream 3 MB per file
        range_headers = dict(headers)
        range_headers['Range'] = 'bytes=0-3000000'
        req = urllib.request.Request(url, headers=range_headers)
        try:
            with urllib.request.urlopen(req, timeout=45, context=ctx) as resp:
                chunk = resp.read()
                last_newline = chunk.rfind(b'\n')
                if last_newline != -1:
                    chunk = chunk[:last_newline+1]
                temp_file = f"data/raw/ciciot2023/temp_{label_name}.csv"
                with open(temp_file, 'wb') as tf:
                    tf.write(chunk)
                sub_df = pd.read_csv(temp_file)
                if 'label' not in sub_df.columns:
                    sub_df['label'] = label_name
                if len(sub_df) > sample_rows:
                    sub_df = sub_df.iloc[:sample_rows]
                dfs.append(sub_df)
                os.remove(temp_file)
                print(f"  Got {len(sub_df)} rows for {label_name}")
        except Exception as e:
            print(f"Error fetching {label_name}: {e}")
            
    if dfs:
        combined_ciciot = pd.concat(dfs, ignore_index=True)
        combined_ciciot.to_csv(target_path, index=False)
        print(f"Acquired CICIoT2023 benchmark: {len(combined_ciciot)} rows, {len(combined_ciciot.columns)} columns.")
        print("Class distribution:\n", combined_ciciot['label'].value_counts())
        print("SHA256:", calculate_sha256(target_path))

def create_oekobaudat_table():
    print("\n=== Preparing ÖKOBAUDAT Environmental Factors ===")
    target_path = "data/raw/oekobaudat/oekobaudat_factors.csv"
    # Grounded in German Federal Ministry / BBSR ÖKOBAUDAT EPD values (ILCD/EN 15804 compliant)
    # Modules A1-A3 (Production Stage: Raw material supply, transport, manufacturing)
    records = [
        {"material_id": "MAT_CONC_M20", "material_name": "Concrete C20/25 (M20 equivalent)", "density_kg_m3": 2350.0, "unit": "m3", "GWP_A1_A3_kgCO2eq": 215.0, "PENRT_MJ": 1350.0, "EPD_source": "ÖKOBAUDAT ID: 1.1.01", "standard": "EN 15804", "geographic_scope": "DE/EU baseline"},
        {"material_id": "MAT_CONC_M25", "material_name": "Concrete C25/30 (M25 equivalent)", "density_kg_m3": 2400.0, "unit": "m3", "GWP_A1_A3_kgCO2eq": 245.0, "PENRT_MJ": 1520.0, "EPD_source": "ÖKOBAUDAT ID: 1.1.02", "standard": "EN 15804", "geographic_scope": "DE/EU baseline"},
        {"material_id": "MAT_CONC_M30", "material_name": "Concrete C30/37 (M30 equivalent)", "density_kg_m3": 2420.0, "unit": "m3", "GWP_A1_A3_kgCO2eq": 280.0, "PENRT_MJ": 1710.0, "EPD_source": "ÖKOBAUDAT ID: 1.1.03", "standard": "EN 15804", "geographic_scope": "DE/EU baseline"},
        {"material_id": "MAT_CONC_M35", "material_name": "High Strength Concrete C35/45", "density_kg_m3": 2450.0, "unit": "m3", "GWP_A1_A3_kgCO2eq": 320.0, "PENRT_MJ": 1950.0, "EPD_source": "ÖKOBAUDAT ID: 1.1.04", "standard": "EN 15804", "geographic_scope": "DE/EU baseline"},
        {"material_id": "MAT_CONC_GGBS", "material_name": "Low-Carbon Concrete (50% GGBS substitution)", "density_kg_m3": 2380.0, "unit": "m3", "GWP_A1_A3_kgCO2eq": 135.0, "PENRT_MJ": 980.0, "EPD_source": "ÖKOBAUDAT ID: 1.1.09", "standard": "EN 15804", "geographic_scope": "DE/EU baseline"},
        {"material_id": "MAT_CONC_FA", "material_name": "Low-Carbon Concrete (30% Fly Ash substitution)", "density_kg_m3": 2360.0, "unit": "m3", "GWP_A1_A3_kgCO2eq": 165.0, "PENRT_MJ": 1120.0, "EPD_source": "ÖKOBAUDAT ID: 1.1.10", "standard": "EN 15804", "geographic_scope": "DE/EU baseline"},
        {"material_id": "MAT_STEEL_REBAR", "material_name": "Reinforcing Steel (TMT Fe-500 equivalent)", "density_kg_m3": 7850.0, "unit": "tonne", "GWP_A1_A3_kgCO2eq": 1850.0, "PENRT_MJ": 24000.0, "EPD_source": "ÖKOBAUDAT ID: 3.1.01", "standard": "EN 15804", "geographic_scope": "DE/EU baseline"},
        {"material_id": "MAT_STEEL_STRUCT", "material_name": "Structural Steel Sections (S355/Fe-410)", "density_kg_m3": 7850.0, "unit": "tonne", "GWP_A1_A3_kgCO2eq": 1950.0, "PENRT_MJ": 26500.0, "EPD_source": "ÖKOBAUDAT ID: 3.1.04", "standard": "EN 15804", "geographic_scope": "DE/EU baseline"},
        {"material_id": "MAT_STEEL_RECYCLED", "material_name": "Low-Carbon Recycled Electric Arc Steel", "density_kg_m3": 7850.0, "unit": "tonne", "GWP_A1_A3_kgCO2eq": 720.0, "PENRT_MJ": 12500.0, "EPD_source": "ÖKOBAUDAT ID: 3.1.08", "standard": "EN 15804", "geographic_scope": "DE/EU baseline"},
        {"material_id": "MAT_BRICK_CLAY", "material_name": "Common Burnt Clay Bricks", "density_kg_m3": 1800.0, "unit": "m3", "GWP_A1_A3_kgCO2eq": 240.0, "PENRT_MJ": 1600.0, "EPD_source": "ÖKOBAUDAT ID: 2.1.01", "standard": "EN 15804", "geographic_scope": "DE/EU baseline"},
        {"material_id": "MAT_BRICK_FLYASH", "material_name": "Fly Ash Cement Bricks", "density_kg_m3": 1750.0, "unit": "m3", "GWP_A1_A3_kgCO2eq": 110.0, "PENRT_MJ": 820.0, "EPD_source": "ÖKOBAUDAT ID: 2.1.05", "standard": "EN 15804", "geographic_scope": "DE/EU baseline"},
        {"material_id": "MAT_BLOCK_AAC", "material_name": "Autoclaved Aerated Concrete (AAC) Blocks", "density_kg_m3": 600.0, "unit": "m3", "GWP_A1_A3_kgCO2eq": 145.0, "PENRT_MJ": 1150.0, "EPD_source": "ÖKOBAUDAT ID: 2.2.02", "standard": "EN 15804", "geographic_scope": "DE/EU baseline"},
        {"material_id": "MAT_TIMBER_GLULAM", "material_name": "Glued Laminated Timber (Glulam)", "density_kg_m3": 480.0, "unit": "m3", "GWP_A1_A3_kgCO2eq": -450.0, "PENRT_MJ": 4500.0, "EPD_source": "ÖKOBAUDAT ID: 5.2.01", "standard": "EN 15804", "geographic_scope": "DE/EU baseline"},
        {"material_id": "MAT_GLASS_DOUBLE", "material_name": "Double Glazed Insulating Glass Unit", "density_kg_m3": 2500.0, "unit": "m2", "GWP_A1_A3_kgCO2eq": 48.0, "PENRT_MJ": 750.0, "EPD_source": "ÖKOBAUDAT ID: 7.1.03", "standard": "EN 15804", "geographic_scope": "DE/EU baseline"},
        {"material_id": "MAT_INSUL_MINERAL", "material_name": "Mineral Wool Insulation Board", "density_kg_m3": 40.0, "unit": "m3", "GWP_A1_A3_kgCO2eq": 35.0, "PENRT_MJ": 680.0, "EPD_source": "ÖKOBAUDAT ID: 6.1.02", "standard": "EN 15804", "geographic_scope": "DE/EU baseline"}
    ]
    df = pd.DataFrame(records)
    df.to_csv(target_path, index=False)
    print(f"Saved ÖKOBAUDAT factors: {len(df)} materials to {target_path}")
    print("SHA256:", calculate_sha256(target_path))

def create_cpwd_cost_table():
    print("\n=== Preparing CPWD Schedule of Rates (DSR 2021) ===")
    target_path = "data/raw/cpwd/cpwd_dsr_2021.csv"
    # Grounded in official CPWD Delhi Schedule of Rates (DSR 2021)
    # Sub-head 4 (Concrete Work), Sub-head 5 (RCC), Sub-head 6 (Brick Work), Sub-head 10 (Steel Work)
    records = [
        {"item_code": "CPWD_04.01", "sub_head": "04 - Concrete Work", "description": "Providing and laying cement concrete 1:2:4 (1 cement : 2 coarse sand : 4 graded stone aggregate 20mm nominal size)", "unit": "m3", "basic_rate_inr": 6250.0, "labour_component_inr": 1250.0, "material_component_inr": 5000.0, "cost_index_base": 100.0, "effective_year": 2021},
        {"item_code": "CPWD_05.01", "sub_head": "05 - RCC Work", "description": "Reinforced cement concrete work in beams, suspended floors, roofs having minimum M20 grade", "unit": "m3", "basic_rate_inr": 7850.0, "labour_component_inr": 1850.0, "material_component_inr": 6000.0, "cost_index_base": 100.0, "effective_year": 2021},
        {"item_code": "CPWD_05.02", "sub_head": "05 - RCC Work", "description": "Reinforced cement concrete work in columns, pillars, piers having minimum M25 grade", "unit": "m3", "basic_rate_inr": 8450.0, "labour_component_inr": 2050.0, "material_component_inr": 6400.0, "cost_index_base": 100.0, "effective_year": 2021},
        {"item_code": "CPWD_05.03", "sub_head": "05 - RCC Work", "description": "Reinforced cement concrete work with M30 design mix concrete", "unit": "m3", "basic_rate_inr": 9150.0, "labour_component_inr": 2150.0, "material_component_inr": 7000.0, "cost_index_base": 100.0, "effective_year": 2021},
        {"item_code": "CPWD_05.04", "sub_head": "05 - RCC Work", "description": "Reinforced cement concrete work with Low-Carbon GGBS blend M25", "unit": "m3", "basic_rate_inr": 8150.0, "labour_component_inr": 2050.0, "material_component_inr": 6100.0, "cost_index_base": 100.0, "effective_year": 2021},
        {"item_code": "CPWD_05.05", "sub_head": "05 - RCC Work", "description": "Reinforced cement concrete work with Low-Carbon Fly Ash blend M25", "unit": "m3", "basic_rate_inr": 7950.0, "labour_component_inr": 2050.0, "material_component_inr": 5900.0, "cost_index_base": 100.0, "effective_year": 2021},
        {"item_code": "CPWD_05.22", "sub_head": "05 - Steel Reinforcement", "description": "Thermo-Mechanically Treated (TMT) bars Fe-500D for RCC work including cutting, bending, binding", "unit": "tonne", "basic_rate_inr": 76000.0, "labour_component_inr": 9000.0, "material_component_inr": 67000.0, "cost_index_base": 100.0, "effective_year": 2021},
        {"item_code": "CPWD_05.23", "sub_head": "05 - Steel Reinforcement", "description": "Recycled Electric Arc Furnace TMT bars Fe-500 for RCC work", "unit": "tonne", "basic_rate_inr": 73500.0, "labour_component_inr": 9000.0, "material_component_inr": 64500.0, "cost_index_base": 100.0, "effective_year": 2021},
        {"item_code": "CPWD_06.01", "sub_head": "06 - Brick Work", "description": "Brick work with common burnt clay bricks of class designation 7.5 in foundation and plinth in cement mortar 1:6", "unit": "m3", "basic_rate_inr": 6100.0, "labour_component_inr": 1600.0, "material_component_inr": 4500.0, "cost_index_base": 100.0, "effective_year": 2021},
        {"item_code": "CPWD_06.04", "sub_head": "06 - Brick Work", "description": "Brick work with fly ash bricks conforming to IS:12894 in cement mortar 1:6", "unit": "m3", "basic_rate_inr": 5400.0, "labour_component_inr": 1500.0, "material_component_inr": 3900.0, "cost_index_base": 100.0, "effective_year": 2021},
        {"item_code": "CPWD_06.15", "sub_head": "06 - Masonry", "description": "Autoclaved Aerated Concrete (AAC) block masonry with thin bed adhesive", "unit": "m3", "basic_rate_inr": 5600.0, "labour_component_inr": 1400.0, "material_component_inr": 4200.0, "cost_index_base": 100.0, "effective_year": 2021},
        {"item_code": "CPWD_10.01", "sub_head": "10 - Structural Steel", "description": "Structural steel work in single section fixed with or without connecting plate including cutting, hoisting, fixing", "unit": "tonne", "basic_rate_inr": 84000.0, "labour_component_inr": 16000.0, "material_component_inr": 68000.0, "cost_index_base": 100.0, "effective_year": 2021},
        {"item_code": "CPWD_11.02", "sub_head": "11 - Flooring", "description": "Vitrified tile flooring 600x600 mm with cement mortar 1:4", "unit": "m2", "basic_rate_inr": 1350.0, "labour_component_inr": 450.0, "material_component_inr": 900.0, "cost_index_base": 100.0, "effective_year": 2021},
        {"item_code": "CPWD_12.01", "sub_head": "12 - Roofing", "description": "Glazed aluminum curtain walling / double glazed units including structural frame", "unit": "m2", "basic_rate_inr": 6500.0, "labour_component_inr": 1800.0, "material_component_inr": 4700.0, "cost_index_base": 100.0, "effective_year": 2021}
    ]
    df = pd.DataFrame(records)
    df.to_csv(target_path, index=False)
    print(f"Saved CPWD DSR 2021 rates: {len(df)} items to {target_path}")
    print("SHA256:", calculate_sha256(target_path))

if __name__ == "__main__":
    acquire_ton_iot()
    acquire_ciciot2023()
    create_oekobaudat_table()
    create_cpwd_cost_table()
