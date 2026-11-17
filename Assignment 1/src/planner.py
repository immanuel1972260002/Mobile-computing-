"""Educational cellular frequency-planning calculator.
Run: python planner.py --self-test
     python planner.py --out ../results
"""
import argparse, csv, json, math
from pathlib import Path

TOTAL_CHANNELS = 420
AREA_KM2 = 12.0
RADIUS_KM = 0.5
TRAFFIC_PER_USER = 0.02
BLOCKING_TARGET = 0.02

def erlang_b(channels, offered):
    """Erlang-B blocking probability using stable recursive evaluation."""
    b = 1.0
    for m in range(1, max(0, int(channels)) + 1):
        b = offered * b / (m + offered * b)
    return b

def capacity_at_blocking(channels, target=BLOCKING_TARGET):
    """Maximum offered Erlangs at or below the target blocking probability."""
    lo, hi = 0.0, max(1.0, channels * 2.0)
    while erlang_b(channels, hi) < target:
        hi *= 2
    for _ in range(70):
        mid = (lo + hi) / 2
        if erlang_b(channels, mid) <= target:
            lo = mid
        else:
            hi = mid
    return lo

def hex_area(radius=RADIUS_KM):
    return 3 * math.sqrt(3) * radius * radius / 2

def valid_cluster_sizes(limit=30):
    vals = set()
    for i in range(int(math.sqrt(limit)) + 2):
        for j in range(int(math.sqrt(limit)) + 2):
            n = i*i + i*j + j*j
            if 1 <= n <= limit:
                vals.add(n)
    return sorted(vals)

def reuse_distance(radius, cluster_size):
    return radius * math.sqrt(3 * cluster_size)

def sir_db(cluster_size, path_loss_n=4.0, interferers=6):
    """Equal-distance first-tier, cell-edge SIR approximation."""
    linear = (3 * cluster_size) ** (path_loss_n / 2) / interferers
    return 10 * math.log10(linear)

def split_capacity(capacity0, rounds, fraction=1.0):
    """Aggregate capacity recurrence for uniform or selective four-way splits."""
    values = [capacity0]
    for _ in range(rounds):
        values.append(values[-1] * (1 + 3 * fraction))
    return values

def dynamic_allocate(neighbours, active, pool):
    """Greedy non-conflicting channel assignment for one request per cell."""
    chosen = {}
    for cell in sorted(neighbours):
        forbidden = set()
        for nb in neighbours[cell]:
            forbidden.update(active.get(nb, set()))
        used = set(active.get(cell, set()))
        channel = next((x for x in pool if x not in forbidden and x not in used), None)
        chosen[cell] = channel
        if channel is not None:
            active.setdefault(cell, set()).add(channel)
    return chosen

def run(out):
    out.mkdir(parents=True, exist_ok=True)
    capacity_rows = []
    for n in (3, 4, 7, 12):
        channels = TOTAL_CHANNELS // n
        per_cell = capacity_at_blocking(channels)
        cells = math.ceil(AREA_KM2 / hex_area())
        for users in (1000, 10000, 20000, 100000):
            demand = users * TRAFFIC_PER_USER
            capacity_rows.append({
                "cluster_size": n, "channels_per_cell": channels,
                "cell_count_ideal": cells, "capacity_per_cell_E": round(per_cell, 4),
                "network_capacity_E": round(cells * per_cell, 4),
                "subscribers": users, "offered_traffic_E": demand,
                "blocking_if_uniform": round(erlang_b(channels, demand / cells), 6)
            })
    with (out / "capacity_experiments.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=capacity_rows[0].keys())
        w.writeheader(); w.writerows(capacity_rows)

    sir_rows = []
    for n in (2.5, 3.0, 4.0):
        for cluster in (3, 4, 7, 12):
            for sectorized in (False, True):
                i0 = 2 if sectorized else 6
                sir_rows.append({"cluster_size": cluster, "path_loss_n": n,
                                 "sectorized_ideal": sectorized,
                                 "dominant_interferers": i0,
                                 "sir_db": round(sir_db(cluster, n, i0), 3)})
    with (out / "sir_experiments.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=sir_rows[0].keys())
        w.writeheader(); w.writerows(sir_rows)

    event_traffic = 25000 * 0.05
    event = {"attendees": 25000, "traffic_each_E": 0.05,
             "event_traffic_E": event_traffic, "event_zone_km2": 1.0,
             "event_density_E_per_km2": event_traffic,
             "township_reference_users": 100000,
             "township_average_density_E_per_km2":
                 (100000 * TRAFFIC_PER_USER) / AREA_KM2,
             "event_duration_hours": 4, "events_per_month": 2}
    (out / "event_surge.json").write_text(json.dumps(event, indent=2))

    split_rows = []
    for k, cap in enumerate(split_capacity(1.0, 4)):
        split_rows.append({"round": k, "relative_cells": 4**k,
                           "relative_capacity": cap, "radius_km": RADIUS_KM/(2**k)})
    with (out / "cell_splitting_recurrence.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=split_rows[0].keys())
        w.writeheader(); w.writerows(split_rows)
    return {"capacity_cases": len(capacity_rows), "sir_cases": len(sir_rows)}

def self_test():
    assert abs(hex_area(1) - 2.598076211) < 1e-6
    assert valid_cluster_sizes(12) == [1, 3, 4, 7, 9, 12]
    assert abs(sir_db(7, 4, 6) - 18.669) < 0.01
    assert erlang_b(10, 1) < 0.01
    assert capacity_at_blocking(60) > 0
    assert split_capacity(1, 2) == [1, 4, 16]
    return "PASS: geometry, reuse, SIR, Erlang-B and splitting recurrence"

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="results")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        print(self_test())
    print(json.dumps(run(Path(args.out)), indent=2))
