from gem5.resources.resource import WorkloadResource, obtain_resource,DiskImageResource
from pathlib import Path

file_path = Path(__file__).resolve().parent

disk_image_base_path = Path(file_path/"../../gem5-resources/src/looppoint-use-disk/")
checkpoint_base_path = Path(file_path/"checkpoints")

def get_arm_npb_workload(workload_name = None, class_size = None, obtain_process_maps = False, start_from_after_boot_checkpoint = False, start_from_workload_checkpoint = False):
    workload = WorkloadResource(
        function = "set_kernel_disk_workload",
        parameters = {
            "kernel" : obtain_resource(resource_id="arm64-linux-kernel-5.15.36"),
            "disk_image" : DiskImageResource(local_path=Path(disk_image_base_path/"arm-disk-image-24-04/arm-24.04-NPB3.4-OMP"),root_partition="2"),
            "bootloader" : obtain_resource(resource_id="arm64-bootloader-foundation")
        }
    )
    if start_from_after_boot_checkpoint:
        workload.set_parameter("checkpoint", Path(checkpoint_base_path/"after-boot-cpts/arm-after-boot-cpt"))
    if workload_name is not None:
        workload.set_parameter("readfile_contents", f"LD_LIBRARY_PATH=/home/gem5/NPB3.4-OMP/common/aarch64-unknown-linux-gnu OMP_NUM_THREADS=8 /home/gem5/NPB3.4-OMP/{workload_name.upper()}/{class_size}/c_m5_fs_naive/aarch64/*.c_m5_fs_naive;")
        if start_from_workload_checkpoint:
            workload.set_parameter("checkpoint", Path(checkpoint_base_path/f"workload-cpts/arm-{workload_name}-{class_size}-cpt"))
    if obtain_process_maps:
        workload.set_parameter("readfile_contents",
f"""#!/bin/bash

# Set environment variables and run the executable in the background
LD_LIBRARY_PATH=/home/gem5/NPB3.4-OMP/common/aarch64-unknown-linux-gnu OMP_NUM_THREADS=8 /home/gem5/NPB3.4-OMP/{workload_name.upper()}/{class_size}/c_m5_fs_naive/aarch64/*.c_m5_fs_naive &

# Capture the process ID of the background process
PID=$!

sleep 1

# Stop the process
kill -SIGSTOP $PID

# Print the process ID
echo "PID is $PID"

# Use sudo to read the process's memory map and write it to a file
echo 12345 | sudo -S cat /proc/$PID/maps > process_map.txt

# Use m5 to write the file and then exit
m5 writefile process_map.txt
m5 exit
"""
                                )
    return workload

def get_x86_npb_workload(workload_name = None, class_size = None, obtain_process_maps = False, start_from_after_boot_checkpoint = False, start_from_workload_checkpoint = False):
    workload =  WorkloadResource(
        function = "set_kernel_disk_workload",
        parameters = {
            "kernel_args" : [
                "earlyprintk=ttyS0",
                "console=ttyS0",
                "lpj=7999923",
                "root=/dev/sda2"
            ],
            "kernel" : obtain_resource("x86-linux-kernel-5.4.0-105-generic"),
            "disk_image" : DiskImageResource(local_path=Path(disk_image_base_path/"x86-disk-image-24-04/x86-24.04-NPB3.4-OMP")),
        }
    )
    if start_from_after_boot_checkpoint:
        workload.set_parameter("checkpoint", Path(checkpoint_base_path/"after-boot-cpts/x86-after-boot-cpt"))
    if workload_name is not None:
        workload.set_parameter("readfile_contents", f"LD_LIBRARY_PATH=/home/gem5/NPB3.4-OMP/common/x86_64-unknown-linux-gnu OMP_NUM_THREADS=8 /home/gem5/NPB3.4-OMP/{workload_name.upper()}/{class_size}/c_m5_fs_naive/x86_64/*.c_m5_fs_naive;")
        if start_from_workload_checkpoint:
            workload.set_parameter("checkpoint", Path(checkpoint_base_path/f"workload-cpts/x86-{workload_name}-{class_size}-cpt"))
    if obtain_process_maps:
        workload.set_parameter("readfile_contents", 
f"""#!/bin/bash

# Set environment variables and run the executable in the background
LD_LIBRARY_PATH=/home/gem5/NPB3.4-OMP/common/x86_64-unknown-linux-gnu OMP_NUM_THREADS=8 /home/gem5/NPB3.4-OMP/{workload_name.upper()}/{class_size}/c_m5_fs_naive/x86_64/*.c_m5_fs_naive &

# Capture the process ID of the background process
PID=$!

sleep 1

# Stop the process
kill -SIGSTOP $PID

# Print the process ID
echo "PID is $PID"

# Use sudo to read the process's memory map and write it to a file
echo 12345 | sudo -S cat /proc/$PID/maps > process_map.txt

# Use m5 to write the file and then exit
m5 writefile process_map.txt
m5 exit
"""
                                )
    return workload

def get_riscv_npb_workload(workload_name = None, class_size = None, obtain_process_maps = False, start_from_after_boot_checkpoint = False, start_from_workload_checkpoint = False):
    workload = WorkloadResource(
        function = "set_kernel_disk_workload",
        parameters = {
            "kernel" : obtain_resource(resource_id="riscv-linux-6.5.5-kernel"),
            "disk_image" : DiskImageResource(local_path=Path(disk_image_base_path/"riscv-disk-image-24-04/riscv-24.04-NPB3.4-OMP")),
            "bootloader" : obtain_resource(resource_id="riscv-bootloader-opensbi-1.3.1")
        }
    )
    if start_from_after_boot_checkpoint:
        workload.set_parameter("checkpoint", Path(checkpoint_base_path/"after-boot-cpts/riscv-after-boot-cpt"))
    if workload_name is not None:
        workload.set_parameter("readfile_contents", f"LD_LIBRARY_PATH=/home/gem5/NPB3.4-OMP/common/riscv64-unknown-linux-gnu OMP_NUM_THREADS=8 /home/gem5/NPB3.4-OMP/{workload_name.upper()}/{class_size}/c_m5_fs_naive/riscv64/*.c_m5_fs_naive;")
        if start_from_workload_checkpoint:
            workload.set_parameter("checkpoint", Path(checkpoint_base_path/f"workload-cpts/riscv-{workload_name}-{class_size}-cpt"))
    if obtain_process_maps:
        workload.set_parameter("readfile_contents", 
f"""#!/bin/bash

# Set environment variables and run the executable in the background
LD_LIBRARY_PATH=/home/gem5/NPB3.4-OMP/common/riscv64-unknown-linux-gnu OMP_NUM_THREADS=8 /home/gem5/NPB3.4-OMP/{workload_name.upper()}/{class_size}/c_m5_fs_naive/riscv64/*.c_m5_fs_naive &

# Capture the process ID of the background process
PID=$!

sleep 1

# Stop the process
kill -SIGSTOP $PID

# Print the process ID
echo "PID is $PID"

# Use sudo to read the process's memory map and write it to a file
echo 12345 | sudo -S cat /proc/$PID/maps > process_map.txt

# Use m5 to write the file and then exit
m5 writefile process_map.txt
m5 exit
"""
                                )
    return workload
