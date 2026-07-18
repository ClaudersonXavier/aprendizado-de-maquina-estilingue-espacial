"""
replay_buffer.py — Salva e carrega experiencias de sucesso do agente.

Formato JSON por run:
  version, run_id, timestamp, stats, checkpoint_order, segments

Cada segmento:
  {"target": [x,y], "waypoints": [[x,y], ...]}
"""

import json
import os
from datetime import datetime

_AGENTS_DIR = os.path.dirname(os.path.abspath(__file__))
SAVE_DIR = os.path.join(_AGENTS_DIR, "..", "training_data")
SAVE_DIR = os.path.normpath(SAVE_DIR)


def get_next_run_id():
    os.makedirs(SAVE_DIR, exist_ok=True)
    existing = [
        f for f in os.listdir(SAVE_DIR)
        if f.startswith("run_") and f.endswith(".json")
    ]
    if not existing:
        return 1
    nums = []
    for f in existing:
        try:
            nums.append(int(f[4:-5]))
        except ValueError:
            pass
    return max(nums) + 1 if nums else 1


def save_run(segments, checkpoint_order, stats):
    run_id = get_next_run_id()
    data = {
        "version": 1,
        "run_id": run_id,
        "timestamp": datetime.now().isoformat(),
        "stats": stats,
        "checkpoint_order": [
            list(cp) for cp in checkpoint_order
        ],
        "segments": [
            {
                "target": list(seg["target"]),
                "waypoints": [list(wp) for wp in seg["waypoints"]],
            }
            for seg in segments
        ],
    }
    path = os.path.join(SAVE_DIR, f"run_{run_id:03d}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    return run_id, path


def load_run(run_id):
    os.makedirs(SAVE_DIR, exist_ok=True)

    if run_id == "latest":
        existing = sorted([
            f for f in os.listdir(SAVE_DIR)
            if f.startswith("run_") and f.endswith(".json")
        ])
        if not existing:
            return None
        run_id = existing[-1][4:-5]

    path = os.path.join(SAVE_DIR, f"run_{int(run_id):03d}.json")
    if not os.path.exists(path):
        return None

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    data["segments"] = [
        {
            "target": tuple(seg["target"]),
            "waypoints": [tuple(wp) for wp in seg["waypoints"]],
        }
        for seg in data["segments"]
    ]
    data["checkpoint_order"] = [
        tuple(cp) for cp in data["checkpoint_order"]
    ]
    return data


def list_runs():
    os.makedirs(SAVE_DIR, exist_ok=True)
    runs = []
    for f in sorted(os.listdir(SAVE_DIR)):
        if f.startswith("run_") and f.endswith(".json"):
            try:
                with open(os.path.join(SAVE_DIR, f), "r",
                          encoding="utf-8") as fp:
                    data = json.load(fp)
                runs.append({
                    "id": data.get("run_id", 0),
                    "timestamp": data.get("timestamp", ""),
                    "reward": data["stats"]["reward"],
                    "steps": data["stats"]["steps"],
                    "thrusts": data["stats"]["thrusts"],
                    "fuel_used": data["stats"]["fuel_used"],
                    "file": f,
                })
            except (json.JSONDecodeError, KeyError):
                pass
    return runs
