import json
from pathlib import Path
import argparse

parser = argparse.ArgumentParser(description="Count the number of regions in the workload")
parser.add_argument("--json-file", help="The json file that contains the workload information", required=True, type=str)
args = parser.parse_args()

with open(args.json_file, "r") as f:
    data = json.load(f)

print(len(data))
