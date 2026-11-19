#!/usr/bin/env python3
"""Reproducible educational mobile-network simulation for Assignment 3.

This is a deterministic analytical model, not a packet-level radio simulator.
Run from the repository root:
    python Assignment\ 3/src/mobile_network_sim.py
It writes CSV and JSON files under Assignment 3/results/.
"""
from __future__ import annotations
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
RESULTS = ROOT / "results"


def read_rows(filename: str) -> list[dict[str, str]]:
    with (DATA / filename).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def mobility_model(row: dict[str, str]) -> dict[str, float | str | int]:
    """Illustrative model: speed and weak coverage increase handoffs/loss/delay."""
    speed = float(row["speed_kmh"])
    overlap = float(row["coverage_overlap_pct"])
    packets = int(row["packets_sent"])
    handoffs = max(0, round(speed / 15))
    interruption_ms = max(5.0, 8.0 + speed * 0.8 - overlap * 0.12)
    loss_pct = min(45.0, max(0.5, 1.0 + speed * 0.22 + (100 - overlap) * 0.12))
    delivered = round(packets * (1 - loss_pct / 100))
    delay_ms = 25.0 + speed * 0.75 + (100 - overlap) * 0.18
    return {
        "scenario": row["scenario"], "speed_kmh": speed, "handoffs": handoffs,
        "interruption_ms": round(interruption_ms, 2),
        "packets_sent": packets, "packets_delivered": delivered,
        "packet_delivery_pct": round(delivered * 100 / packets, 2),
        "estimated_delay_ms": round(delay_ms, 2),
    }


def routing_model(row: dict[str, str]) -> dict[str, float | str | int]:
    """Compare illustrative AODV/DSDV costs under identical network conditions."""
    nodes = int(row["nodes"])
    mobility = float(row["mobility_index"])
    traffic = float(row["traffic_packets"])
    # Control-message counts are relative model units, not protocol wire counts.
    aodv_control = round(2.0 * nodes + 1.8 * mobility * nodes + 0.08 * traffic)
    dsdv_control = round(5.0 * nodes + 0.7 * mobility * nodes + 0.03 * traffic)
    aodv_delay = 18.0 + 1.7 * mobility + (12.0 if traffic == 0 else 0.0)
    dsdv_delay = 12.0 + 0.9 * mobility
    aodv_delivery = max(65.0, 98.0 - 0.55 * mobility - nodes * 0.12)
    dsdv_delivery = max(68.0, 97.0 - 0.42 * mobility - nodes * 0.10)
    return {
        "scenario": row["scenario"], "nodes": nodes, "mobility_index": mobility,
        "traffic_packets": int(traffic),
        "aodv_control_units": aodv_control, "dsdv_control_units": dsdv_control,
        "aodv_delay_ms": round(aodv_delay, 2), "dsdv_delay_ms": round(dsdv_delay, 2),
        "aodv_delivery_pct": round(aodv_delivery, 2),
        "dsdv_delivery_pct": round(dsdv_delivery, 2),
    }


def write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    RESULTS.mkdir(parents=True, exist_ok=True)
    mobility = [mobility_model(row) for row in read_rows("mobility_scenarios.csv")]
    routing = [routing_model(row) for row in read_rows("routing_scenarios.csv")]
    write_csv(RESULTS / "mobility_results.csv", mobility)
    write_csv(RESULTS / "routing_comparison.csv", routing)

    # Q7 test matrix: same model with node count and mobility varied.
    emergency = []
    for row in routing:
        emergency.append({
            "test_case": row["scenario"], "mobile_nodes": row["nodes"],
            "mobility_index": row["mobility_index"],
            "selected_protocol": "AODV" if row["mobility_index"] >= 5 else "DSDV",
            "aodv_control_units": row["aodv_control_units"],
            "dsdv_control_units": row["dsdv_control_units"],
            "aodv_delay_ms": row["aodv_delay_ms"],
            "aodv_delivery_pct": row["aodv_delivery_pct"],
        })
    write_csv(RESULTS / "emergency_test_results.csv", emergency)

    summary = {
        "model": "deterministic illustrative analytical model",
        "not_a_packet_level_simulator": True,
        "mobility_scenarios": len(mobility),
        "routing_scenarios": len(routing),
        "interpretation": (
            "Compare trends under stated assumptions only; values are not measured "
            "radio-network or ns-3 results."
        ),
        "files": [
            "mobility_results.csv", "routing_comparison.csv",
            "emergency_test_results.csv"
        ],
    }
    (RESULTS / "summary.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8"
    )
    print(f"Generated {len(mobility)} mobility rows and {len(routing)} routing rows.")
    print(f"Results directory: {RESULTS}")


if __name__ == "__main__":
    main()
