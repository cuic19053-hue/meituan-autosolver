import random
import hashlib


def parse_seed_file(file_path: str) -> list[dict]:
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except UnicodeDecodeError:
        try:
            with open(file_path, "r", encoding="gbk") as f:
                lines = f.readlines()
        except UnicodeDecodeError:
            with open(file_path, "r", encoding="latin-1") as f:
                lines = f.readlines()
    except FileNotFoundError:
        print(f"[ERROR] File not found: {file_path}")
        raise FileNotFoundError(f"Seed file not found: {file_path}")

    rows = []
    for line in lines[1:]:
        parts = line.strip().split("\t")
        if len(parts) < 4:
            continue
        task_id_str = parts[0].strip()
        courier_id = parts[1].strip()
        total_score = parts[2].strip()
        willingness = parts[3].strip()
        task_ids = [tid.strip() for tid in task_id_str.split(",") if tid.strip()]
        rows.append({
            "task_ids": task_ids,
            "courier_id": courier_id,
            "score": float(total_score),
            "willingness": float(willingness),
        })

    all_task_ids = set()
    all_courier_ids = set()
    for row in rows:
        all_task_ids.update(row["task_ids"])
        all_courier_ids.add(row["courier_id"])

    print(
        f"[INFO] Parsed seed file: {file_path} | "
        f"Rows: {len(rows)} | "
        f"Unique TaskIDs: {len(all_task_ids)} | "
        f"Unique CourierIDs: {len(all_courier_ids)}"
    )

    return rows


def assign_coordinates(
    task_ids: set[str], courier_ids: set[str]
) -> dict[str, tuple[int, int]]:
    result = {}

    for tid in task_ids:
        seed = int(hashlib.md5(tid.encode()).hexdigest(), 16)
        rng = random.Random(seed)
        x = rng.randint(200, 800)
        y = rng.randint(200, 800)
        result[tid] = (x, y)

    for cid in courier_ids:
        seed = int(hashlib.md5(cid.encode()).hexdigest(), 16)
        rng = random.Random(seed)
        if rng.random() < 0.5:
            x = rng.randint(0, 300)
        else:
            x = rng.randint(700, 1000)
        if rng.random() < 0.5:
            y = rng.randint(0, 300)
        else:
            y = rng.randint(700, 1000)
        result[cid] = (x, y)

    return result


def build_graph_data(file_path: str) -> dict:
    rows = parse_seed_file(file_path)

    all_task_ids = set()
    all_courier_ids = set()
    for row in rows:
        all_task_ids.update(row["task_ids"])
        all_courier_ids.add(row["courier_id"])

    coordinates = assign_coordinates(all_task_ids, all_courier_ids)

    nodes = []
    for tid in all_task_ids:
        x, y = coordinates[tid]
        nodes.append({"id": tid, "type": "task", "x": x, "y": y})
    for cid in all_courier_ids:
        x, y = coordinates[cid]
        nodes.append({"id": cid, "type": "courier", "x": x, "y": y})

    links = []
    for row in rows:
        links.append({
            "source": row["courier_id"],
            "target": row["task_ids"],
            "score": row["score"],
            "willingness": row["willingness"],
        })

    return {"nodes": nodes, "links": links}
