from pathlib import Path
import json
import re
import argparse

parser = argparse.ArgumentParser(description="Extract LoopPoint needed information from the m5out")
parser.add_argument("--m5out-base-dir", help="The path to the m5out directory", required=True, type=str)
parser.add_argument("--output-dir", help="The directory to store the extracted information", required=True, type=str)
args = parser.parse_args()

def parse_all_addresses(file_path):
    all_objects = {}
    with open(file_path) as f:
        data = f.readlines()
        for line in data:
            line_data = line.split()
            if len(line_data) < 6:
                continue
            # print(line_data)
            start_addr = line_data[0].split("-")[0]
            end_addr = line_data[0].split("-")[1]
            permission = line_data[1]
            object = line_data[5]
            object_name = object.split("/")[-1]
            if object_name not in all_objects:
                all_objects[object_name] = {}
            if permission not in all_objects[object_name]:
                all_objects[object_name][permission] = []
            all_objects[object_name][permission].append((start_addr, end_addr))
    return all_objects

def translate_isa_name_to_arch_name(isa):
    if isa == "x86":
        return "x86_64"
    elif isa == "arm":
        return "aarch64"
    elif isa == "riscv":
        return "riscv64"
    else:
        return isa
    
omp_related_libraries_keywords = [
    "omp",
    "libarcher",
    "pthread"
]

m5_out_base_dir = Path(args.m5out_base_dir)
output_dir = Path(args.output_dir)

all_info = {}

for workload_dir in m5_out_base_dir.iterdir():
    dir_name = workload_dir.name
    isa = dir_name.split("-")[0]
    arch = translate_isa_name_to_arch_name(isa)
    workload = dir_name.split("-")[1]
    size = dir_name.split("-")[2]
    address_info = parse_all_addresses(Path(workload_dir/"process_map.txt"))
    target_key = None
    for key in address_info.keys():
        if f"{workload}_{arch}" in key:
            target_key = key
            break
    exec_info = address_info[target_key]["r-xp"]
    start_source_addr = f"0x{exec_info[0][0]}"
    end_source_addr = "0x0"
    for addr in exec_info:
        if int(addr[0],16) < int(start_source_addr,0):
            start_source_addr = f"0x{addr[0]}"
        if int(addr[1],16) > int(end_source_addr,0):
            end_source_addr = f"0x{addr[1]}"
    source_address_range = (start_source_addr, end_source_addr)
    target_key = None
    restricted_address_ranges = []
    for key in address_info.keys():
        for keyword in omp_related_libraries_keywords:
            if keyword in key:
                # print(key)
                for permission, address_ranges in address_info[key].items():
                    for address_range in address_ranges:
                        restricted_address_ranges.append((f"0x{address_range[0]}", f"0x{address_range[1]}"))
                # print(restricted_address_ranges)

    all_info[workload] = {
        "source_address_range" : source_address_range,
        "restricted_address_ranges" : restricted_address_ranges
    }
    print(f"Finish processing {workload}")

with open(output_dir/f"{isa}-NPB-{size}-process-map-info.json", "w") as f:
    json.dump(all_info, f, indent=4)

print(f"Saved the extracted information to the output directory {isa}-NPB-{size}-process-map-info.json")

