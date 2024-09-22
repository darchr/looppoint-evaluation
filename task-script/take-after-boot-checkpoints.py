import subprocess
from multiprocessing import Pool
from pathlib import Path
import argparse
import shutil

parser = argparse.ArgumentParser(description="Take checkpoints at workbegin for NPB workloads")
parser.add_argument("--gem5-base-path", help="The path to the gem5 base directory", required=True, type=str)
parser.add_argument("--arch", help="The architecture to run the workloads on", required=True, type=str)
parser.add_argument("--max-threads", help="The maximum number of threads to use", required=False, type=int, default=8)
parser.add_argument("--output-dir", help="The directory to store the m5outs", required=True, type=str)
args = parser.parse_args()

gem5_base_path = Path(args.gem5_base_path)
max_threads = args.max_threads
arch = args.arch
output_dir = Path(args.output_dir)
output_dir = Path(output_dir/arch)

if arch == "riscv":
    gem5_bin = Path(gem5_base_path/"RISCV_MESI_Two_Level/gem5.fast")
elif arch == "x86":
    gem5_bin = Path(gem5_base_path/"X86_MESI_Three_Level/gem5.fast")
elif arch == "arm":
    gem5_bin = Path(gem5_base_path/"ARM/gem5.opt")

if output_dir.exists():
    shutil.rmtree(output_dir)
output_dir.mkdir(parents=True)

workdir = Path().cwd()
checkpoint_output_path = Path(workdir/"script/workloads/checkpoints/after-boot-cpts")
if not checkpoint_output_path.exists():
    checkpoint_output_path.mkdir(parents=True)

def run(info):
    arch = info["arch"]
    command = info["command"]
    result = subprocess.run(command)
    if result.returncode != 0:
        print(f"Failed to take checkpoint for {arch}")
    else:
        print(f"Successfully took checkpoint for {arch}")
    return result

all_runs = []

run_file = Path(workdir/f"script/pre-experiment/take-after-boot-checkpoints.py")
run_output = Path(output_dir/f"take-after-boot-checkpoint-m5out")
command = [gem5_bin.as_posix(), "-re", "--outdir", run_output.as_posix(), run_file.as_posix(),
            "--checkpoint-output-dir", checkpoint_output_path.as_posix(), "--arch", arch]
all_runs.append({"arch": arch, "command": command})

with Pool(args.max_threads) as p:
    results = p.map(run, all_runs)
    print(results)

print("All Done!")
