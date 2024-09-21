from gem5.resources.resource import WorkloadResource, obtain_resource,DiskImageResource
from pathlib import Path

file_path = Path(__file__).resolve().parent

disk_image_base_path = Path(file_path/"../../gem5-resources/src/looppoint-use-disk/")

def get_arm_npb_workload(workload_name = None, class_size = None):
    workload = WorkloadResource(
        function = "set_kernel_disk_workload",
        parameters = {
            "kernel" : obtain_resource(resource_id="arm64-linux-kernel-5.15.36"),
            "disk_image" : DiskImageResource(local_path=Path(disk_image_base_path/"arm-disk-image-24-04/arm-24.04-NPB3.4-OMP"),root_partition="2"),
            "bootloader" : obtain_resource(resource_id="arm64-bootloader-foundation")
        }
        
    )
    if workload_name is not None:
        workload.set_parameter("readfile_contents", f"echo 12345 | sudo -S -E LD_LIBRARY_PATH=/home/gem5/NPB3.4-OMP/common/aarch64-unknown-linux-gnu OMP_NUM_THREADS=8 /home/gem5/NPB3.4-OMP/{workload_name.upper()}/{class_size}/c_m5_fs_naive/aarch64/*.c_m5_fs_naive;")
    return workload

def get_x86_npb_workload(workload_name = None, class_size = None):
    workload =  WorkloadResource(
        function = "set_kernel_disk_workload",
        parameters = {
            "kernel" : obtain_resource(resource_id="x86-linux-kernel-6.8.0-35-generic"),
            "disk_image" : DiskImageResource(local_path=Path(disk_image_base_path/"x86-disk-image-24-04/x86-24.04-NPB3.4-OMP")),
        }
    )
    if workload_name is not None:
        workload.set_parameter("readfile_contents", f"echo 12345 | sudo -S -E LD_LIBRARY_PATH=/home/gem5/NPB3.4-OMP/common/x86_64-unknown-linux-gnu OMP_NUM_THREADS=8 /home/gem5/NPB3.4-OMP/{workload_name.upper()}/{class_size}/c_m5_fs_naive/x86_64/*.c_m5_fs_naive;")
    return workload

def get_riscv_npb_workload(workload_name = None, class_size = None):
    workload = WorkloadResource(
        function = "set_kernel_disk_workload",
        parameters = {
            "kernel" : obtain_resource(resource_id="riscv-linux-6.5.5-kernel"),
            "disk_image" : DiskImageResource(local_path=Path(disk_image_base_path/"riscv-disk-image-24-04/riscv-24.04-NPB3.4-OMP")),
            "bootloader" : obtain_resource(resource_id="riscv-bootloader-opensbi-1.3.1")
        }
    )
    if workload_name is not None:
        workload.set_parameter("readfile_contents", f"echo 12345 | sudo -S -E LD_LIBRARY_PATH=/home/gem5/NPB3.4-OMP/common/riscv64-unknown-linux-gnu OMP_NUM_THREADS=8 /home/gem5/NPB3.4-OMP/{workload_name.upper()}/{class_size}/c_m5_fs_naive/riscv64/*.c_m5_fs_naive;")
    return workload

