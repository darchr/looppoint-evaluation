import subprocess
from multiprocessing import Pool
from pathlib import Path
import argparse
import shutil
import json

parser = argparse.ArgumentParser(description="Take checkpoints at looppoint marker for NPB workloads")
parser.add_argument("--gem5-base-path", help="The path to the gem5 base directory", required=True, type=str)
parser.add_argument("--arch", help="The architecture to run the workloads on", required=True, type=str)
parser.add_argument("--max-threads", help="The maximum number of threads to use", required=False, type=int, default=8)
parser.add_argument("--output-dir", help="The directory to store the m5outs", required=True, type=str)
parser.add_argument("--looppoint-info-json", help="The json file that contains the looppoint marker information", required=True, type=str)
args = parser.parse_args()

gem5_base_path = Path(args.gem5_base_path)
max_threads = args.max_threads
arch = args.arch
output_dir = Path(args.output_dir)
output_dir = Path(output_dir/arch)
# benchmarks = ["bt", "cg", "ep", "ft", "is", "lu", "mg", "sp"]
# benchmarks = ["cg", "ft", "is", "ep", "mg", "sp"]
benchmarks = ["is", "mg", "ep"]
looppoint_info_json = Path(args.looppoint_info_json)

if arch == "riscv":
    gem5_bin = Path(gem5_base_path/"RISCV_MESI_Two_Level/gem5.fast")
elif arch == "x86":
    gem5_bin = Path(gem5_base_path/"X86_MESI_Two_Level/gem5.fast")
elif arch == "arm":
    gem5_bin = Path(gem5_base_path/"ARM_CHI/gem5.fast")

output_dir.mkdir(parents=True, exist_ok=True)

def run(info):
    bench = info["bench"]
    arch = info["arch"]
    command = info["command"]
    result = subprocess.run(command)
    if result.returncode != 0:
        print(f"Failed to run {bench} {arch}")
    else:
        print(f"Successfully ran {bench} {arch}")
    return result

workdir = Path().cwd()

with open(looppoint_info_json, "r") as f:
    looppoint_info = json.load(f)

all_runs = []
for bench in benchmarks:
    run_file = Path(workdir/f"script/looppoint-restore/looppoint-restore.py")
    for rid in looppoint_info[arch][bench].keys():
        run_output = Path(output_dir/f"{arch}-{bench}-{rid}-restore-m5out")
        command = [gem5_bin.as_posix(), "-re", "--outdir", run_output.as_posix(), run_file.as_posix(),
                    "--workload", bench, "--arch", arch,
                    "--looppoint-info-json", looppoint_info_json.as_posix(),
                    "--rid", rid]
        all_runs.append({"bench": bench, "arch": arch, "command": command})

with Pool(args.max_threads) as p:
    results = p.map(run, all_runs)
    print(results)

print("All Done!")
