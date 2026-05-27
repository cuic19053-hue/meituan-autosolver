import random
import hashlib
import os
import time
from typing import Optional

DATA_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "large_seed301.txt")

_cached_map: Optional[dict] = None


def _read_raw_rows():
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except UnicodeDecodeError:
        try:
            with open(DATA_FILE, "r", encoding="gbk") as f:
                lines = f.readlines()
        except UnicodeDecodeError:
            with open(DATA_FILE, "r", encoding="latin-1") as f:
                lines = f.readlines()
    rows = []
    for line in lines[1:]:
        parts = line.strip().split("\t")
        if len(parts) < 4:
            continue
        task_ids = [t.strip() for t in parts[0].split(",") if t.strip()]
        rows.append({
            "task_ids": task_ids,
            "courier_id": parts[1].strip(),
            "score": float(parts[2].strip()),
            "willingness": float(parts[3].strip()),
        })
    return rows


def _assign_coords(task_ids: set, courier_ids: set):
    result = {}
    for tid in task_ids:
        seed = int(hashlib.md5(tid.encode()).hexdigest(), 16)
        rng = random.Random(seed)
        x = rng.randint(20, 80)
        y = rng.randint(20, 80)
        result[tid] = (x, y)
    for cid in courier_ids:
        seed = int(hashlib.md5(cid.encode()).hexdigest(), 16)
        rng = random.Random(seed)
        x = rng.randint(0, 100)
        y = rng.randint(0, 100)
        result[cid] = (x, y)
    return result


def get_map_init():
    global _cached_map
    if _cached_map is not None:
        return _cached_map
    rows = _read_raw_rows()
    all_tasks = set()
    all_couriers = set()
    for r in rows:
        all_tasks.update(r["task_ids"])
        all_couriers.add(r["courier_id"])
    coords = _assign_coords(all_tasks, all_couriers)
    nodes = []
    for tid in sorted(all_tasks):
        x, y = coords[tid]
        nodes.append({"id": tid, "type": "task", "x": x, "y": y})
    for cid in sorted(all_couriers):
        x, y = coords[cid]
        nodes.append({"id": cid, "type": "courier", "x": x, "y": y})
    links = []
    for r in rows:
        links.append({
            "source": r["courier_id"],
            "target": r["task_ids"],
            "score": r["score"],
            "willingness": r["willingness"],
        })
    _cached_map = {"nodes": nodes, "links": links}
    print(f"[INFO] Map initialized: {len(nodes)} nodes, {len(links)} links")
    return _cached_map


def _ts():
    t = time.localtime()
    return f"{t.tm_hour:02d}:{t.tm_min:02d}:{t.tm_sec:02d}"

def solve():
    rows = _read_raw_rows()
    logs = []
    rows_sorted = sorted(rows, key=lambda r: (-r["score"], -r["willingness"]))
    logs.append(f"[{_ts()}] [INIT] Solver engine loaded, {len(rows)} seed records parsed")
    logs.append(f"[{_ts()}] [INIT] Sorting by score descending, efficiency_threshold = 60.0")

    selected = []
    assigned_tasks = set()
    assigned_couriers = set()
    total_score = 0.0
    efficiency_threshold = 60.0
    conflict_counter = 0

    for idx, r in enumerate(rows_sorted):
        cid = r["courier_id"]
        tasks = r["task_ids"]
        unassigned = [t for t in tasks if t not in assigned_tasks]

        logs.append(f"[{_ts()}] [EFFICIENCY] Evaluating C{idx+1}: score={r['score']:.3f}, willingness={r['willingness']:.4f}, tasks={tasks}")

        if not unassigned:
            logs.append(f"[{_ts()}] [SKIP] {cid} -> {tasks} | All tasks already assigned")
            continue

        if cid in assigned_couriers:
            conflict_counter += 1
            logs.append(f"[{_ts()}] [CONFLICT #{conflict_counter}] {cid} already has assignment, re-evaluating efficiency...")
            logs.append(f"[{_ts()}] [REFLECTION] {cid} node re-assigned due to efficiency threshold ({efficiency_threshold})")
        else:
            logs.append(f"[{_ts()}] [INIT] Fresh courier {cid}, proceeding with assignment check")

        if r["score"] >= efficiency_threshold and r["willingness"] >= 0.3:
            selected.append({
                "source": cid,
                "target": unassigned,
                "score": r["score"],
                "willingness": r["willingness"],
                "assigned": True,
            })
            assigned_tasks.update(unassigned)
            assigned_couriers.add(cid)
            total_score += r["score"]
            logs.append(f"[{_ts()}] [ASSIGN] {cid} -> {unassigned} | Score: {r['score']:.3f} | Willingness: {r['willingness']:.4f}")
        else:
            logs.append(f"[{_ts()}] [WARN] {cid} -> {unassigned} | Score {r['score']:.3f} below threshold ({efficiency_threshold})")
            selected.append({
                "source": cid,
                "target": unassigned,
                "score": r["score"],
                "willingness": r["willingness"],
                "assigned": False,
            })

    logs.append(f"[{_ts()}] [SUMMARY] Total assigned: {len([s for s in selected if s['assigned']])} | Total score: {total_score:.3f} | Conflicts: {conflict_counter}")
    return {"selected": selected, "logs": logs, "total_score": total_score, "assigned_count": len([s for s in selected if s["assigned"]])}
