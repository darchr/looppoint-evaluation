from pathlib import Path
from sklearn.cluster import KMeans
import json
import random
from scipy.spatial import distance
from sklearn.metrics import pairwise_distances
import numpy as np
from sklearn import random_projection

random_seed = 627
np.random.seed(random_seed)
random.seed(random_seed)

# there are three steps to find the looppoints
# 1. form a bbv for each region
# 2. cluster the bbvs
# 3. find the marker for the selected cluster

# 1. form a bbv for each region

def form_bbv_for_region(regional_data, bb_id_map):
    bb_inst_map = regional_data["bb_inst_map"]
    local_bbvs = regional_data["locals"]
    global_inst_length = regional_data["global_length"]
    num_cores = len(local_bbvs)
    bbv = [0 for _ in range(num_cores*len(bb_id_map.keys()))]
    for core_index, local_bbv in enumerate(local_bbvs):
        id_base = core_index*len(bb_id_map.keys())
        for pc, count in local_bbv.items():
            bb_id = bb_id_map[pc]
            bb_inst = bb_inst_map[pc]
            bbv[id_base+bb_id] += (count * bb_inst)/global_inst_length
    return bbv

def form_bb_id_map(last_bb_inst_map):
    bb_id_map = {}
    for pc, _ in last_bb_inst_map.items():
        if pc not in bb_id_map:
            bb_id_map[pc] = len(bb_id_map.keys())
    return bb_id_map

def form_bbvs_for_workload(workload_json_path):
    with open(workload_json_path, "r") as f:
        workload_data = json.load(f)
    total_regions = len(workload_data)
    bb_id_map = form_bb_id_map(workload_data[str(total_regions-1)]["bb_inst_map"])
    all_bbvs = []
    for region_id in range(total_regions):
        regional_data = workload_data[str(region_id)]
        bbv = form_bbv_for_region(regional_data, bb_id_map)
        all_bbvs.append(bbv)
    return all_bbvs

# 2. cluster the bbvs

def find_rep_rid(data, labels, centers):
    rep_rid = {}
    for i, center in enumerate(centers):
        min = float('inf')
        min_rid = -1
        count = 0
        for j, label in enumerate(labels):
            if label == i:
                count += 1
                dist = distance.euclidean(center, data[j])
                if dist < min:
                    min = dist
                    min_rid = j
        if min_rid != -1:
            rep_rid[i] = min_rid
        else:
            print("Error: No representative RID found for cluster")
            print(f"There are {count} RIDs in cluster {i}")

    return rep_rid

def find_cluster_rid(labels):
    clusters = {}
    for i, label in enumerate(labels):
        if str(label) not in clusters.keys():
            clusters[str(label)] = []
        clusters[str(label)].append(i)
    return clusters

def cluster_bbvs(all_bbvs, num_clusters):
    kmeans = KMeans(n_clusters=num_clusters, random_state=random_seed)
    kmeans.fit(all_bbvs)

    centers = kmeans.cluster_centers_
    labels = kmeans.labels_
    inertia = kmeans.inertia_
    n_iter = kmeans.n_iter_
    rep_rid = find_rep_rid(all_bbvs, labels.tolist(), centers.tolist())
    clusters = find_cluster_rid(labels.tolist())
    return {
        "centers": centers.tolist(),
        "labels": labels.tolist(),
        "inertia": inertia,
        "n_iter": n_iter,
        "rep_rid": rep_rid,
        "clusters": clusters
    }

def random_linear_projection(data, num_projections):
    transformer = random_projection.GaussianRandomProjection(
        random_state=random_seed, 
        n_components=num_projections
    )
    return transformer.fit_transform(data)

# 3. find the marker for the selected cluster

def find_marker_for_rid(rid, all_data):
    warmup_rid = rid - 2
    start_rid = rid - 1
    warmup_pc = None
    warmup_count = 0
    start_pc = None
    start_count = 0
    end_data = all_data[str(rid)]
    end_pc = end_data["most_recent_loop"]
    end_count = end_data["most_recent_loop_count"]
    if start_rid >= 0:
        start_data = all_data[str(start_rid)]
        start_pc = start_data["most_recent_loop"]
        start_count = start_data["most_recent_loop_count"]
    if warmup_rid >= 0:
        warmup_data = all_data[str(warmup_rid)]
        warmup_pc = warmup_data["most_recent_loop"]
        warmup_count = warmup_data["most_recent_loop_count"]

    if start_rid >= 0 and warmup_rid >= 0:
        if start_pc in warmup_data["global_loop_counter"]:
            start_count = start_count - warmup_data["global_loop_counter"][start_pc]
        if end_pc in warmup_data["global_loop_counter"]:
            end_count = end_count - warmup_data["global_loop_counter"][end_pc]
    elif start_rid >= 0:
        if end_pc in start_data["global_loop_counter"]:
            end_count = end_count - start_data["global_loop_counter"][end_pc]

    return {
        "warmup_pc": warmup_pc,
        "warmup_count": warmup_count,
        "start_pc": start_pc,
        "start_count": start_count,
        "end_pc": end_pc,
        "end_count": end_count
    }

# main section

benchmarks = ["cg", "ft", "is", "ep", "mg", "sp"]
# bt lu have not finished yet
archs = ["x86", "arm"]
m5out_dir = Path(Path().cwd()/"m5outs/looppoint-analysis")
num_clusters = 30
num_projections = 100
clustered_data = {}
looppoint_markers = {}

for arch in archs:
    clustered_data[arch] = {}
    looppoint_markers[arch] = {}
    for bench in benchmarks:
        bench_m5out_dir = Path(m5out_dir/f"{arch}/{bench}-B-looppoint-analysis.json")
        with open(bench_m5out_dir, "r") as f:
            all_data = json.load(f)
        all_bbvs = form_bbvs_for_workload(bench_m5out_dir)
        projected_all_bbvs = random_linear_projection(all_bbvs, num_projections)
        bench_clusters = num_clusters
        while bench_clusters * 4 > len(all_bbvs):
            bench_clusters -= 5
        if bench_clusters <= 0:
            raise RuntimeError(f"Error: {bench} has too few regions to cluster")
        clustered_data[arch][bench] = cluster_bbvs(projected_all_bbvs, bench_clusters)
        rep_rids = clustered_data[arch][bench]["rep_rid"].values()
        bench_markers = {}
        for rid in rep_rids:
            marker = find_marker_for_rid(rid, all_data)
            bench_markers[rid] = marker
        looppoint_markers[arch][bench] = bench_markers
        print(f"Finished {arch} {bench} with {bench_clusters} clusters")

with open("clustered_data.json", "w") as f:
    json.dump(clustered_data, f, indent=4)    

with open("looppoint_markers.json", "w") as f:
    json.dump(looppoint_markers, f, indent=4)

