import time
import random


def solve(input_text: str) -> list:
    if not input_text or not input_text.strip():
        return []

    lines = input_text.split('\n')
    start = 1 if lines and lines[0][:12] == "task_id_list" else 0
    if len(lines) - start < 1:
        return []

    candidates = []
    push = candidates.append
    task_set = set()
    cost_lookup = {}

    for line in lines[start:]:
        parts = line.split('\t')
        if len(parts) < 3:
            continue
        ts = parts[0]
        c = parts[1]
        try:
            sc = float(parts[2])
        except ValueError:
            continue
        wl = float(parts[3]) if len(parts) >= 4 else 0.0
        tc = ts.count(',') + 1
        cost_val = sc * (2.0 - wl)
        push((ts, c, sc, wl, tc, cost_val))
        task_set.update(ts.split(','))
        cost_lookup[(ts, c)] = cost_val

    n = len(candidates)
    if n == 0:
        return []
    task_count = len(task_set)
    penalty = 100.0
    TIME_BUDGET = 0.80
    t_start = time.perf_counter()

    def _check_time():
        return time.perf_counter() - t_start > TIME_BUDGET

    cpt = [cand[5] / cand[4] for cand in candidates]
    scores_list = [cand[2] for cand in candidates]
    conflict_keys = [(-cand[4], cand[2]) for cand in candidates]
    max_cov_keys = [(-candidates[i][4], cpt[i]) for i in range(n)]

    courier_indices = {}
    for idx, cand in enumerate(candidates):
        ci = courier_indices.setdefault(cand[1], [])
        ci.append(idx)

    courier_min_cpt = {}
    for idx, cand in enumerate(candidates):
        v = cpt[idx]
        if cand[1] not in courier_min_cpt or v < courier_min_cpt[cand[1]]:
            courier_min_cpt[cand[1]] = v
    courier_keys = [(courier_min_cpt[cand[1]], cpt[i]) for i, cand in enumerate(candidates)]

    def _run_greedy(indices):
        ac = set()
        at = set()
        sol = []
        total_cost = 0.0
        for idx in indices:
            cand = candidates[idx]
            ts, c = cand[0], cand[1]
            if c in ac:
                continue
            parts = ts.split(',')
            conflict = False
            for t in parts:
                if t in at:
                    conflict = True
                    break
            if conflict:
                continue
            ac.add(c)
            at.update(parts)
            sol.append((ts, [c]))
            total_cost += cost_lookup[(ts, c)]
        return sol, total_cost + penalty * (task_count - len(at))

    best_score = float('inf')
    best_sol = []

    all_key_sets = [cpt, conflict_keys, scores_list, max_cov_keys, courier_keys]

    for keys in all_key_sets:
        if _check_time():
            break
        indices = sorted(range(n), key=keys.__getitem__)
        sol, sc = _run_greedy(indices)
        if sc < best_score:
            best_score = sc
            best_sol = sol

    remaining = TIME_BUDGET - (time.perf_counter() - t_start)
    if n < 5000 and remaining > 0.03:
        rng = random.Random(42)
        iterations = min(15, int(remaining / 0.01))
        for _ in range(iterations):
            if _check_time():
                break
            jitter = rng.uniform(0.2, 0.9)
            sk = [cpt[i] + rng.uniform(-jitter, jitter) for i in range(n)]
            indices = sorted(range(n), key=sk.__getitem__)
            sol, sc = _run_greedy(indices)
            if sc < best_score:
                best_score = sc
                best_sol = sol

    if best_sol and time.perf_counter() - t_start < TIME_BUDGET * 0.50:
        best_sol = _singleton_merge(best_sol, candidates, courier_indices,
                                    cost_lookup, penalty, t_start, TIME_BUDGET)

    return best_sol


def _singleton_merge(sol, candidates, courier_indices, cost_lookup,
                     penalty, t_start, TIME_BUDGET):
    current = list(sol)
    if len(current) < 2:
        return current

    assigned_ids = {cl[0] for _, cl in current}
    courier_best = {}

    for c_id in assigned_ids:
        best_for_courier = {}
        for idx in courier_indices.get(c_id, ()):
            cand = candidates[idx]
            task_key = ','.join(sorted(cand[0].split(',')))
            cost = cand[5]
            if task_key not in best_for_courier or cost < best_for_courier[task_key][1]:
                best_for_courier[task_key] = (idx, cost)
        courier_best[c_id] = best_for_courier

    improved = True
    iterations = 0

    while improved and iterations < 5:
        if time.perf_counter() - t_start > TIME_BUDGET * 0.88:
            break
        improved = False
        iterations += 1

        singletons = [(i, ts, cl[0]) for i, (ts, cl) in enumerate(current)
                      if ts.count(',') == 0]
        multis = [(i, ts, cl[0]) for i, (ts, cl) in enumerate(current)
                  if ts.count(',') > 0]

        ns = len(singletons)
        nm = len(multis)
        best_benefit = 0
        best_action = None

        for si in range(ns):
            si_idx, sts, scourier = singletons[si]
            scost = cost_lookup[(sts, scourier)]

            for sj in range(si + 1, ns):
                sj_idx, sts2, scourier2 = singletons[sj]
                if scourier == scourier2:
                    continue
                merged_key = ','.join(sorted([sts, sts2]))
                old_total = scost + cost_lookup[(sts2, scourier2)]

                for courier_id, pos, cur_ts in [(scourier, si_idx, sts),
                                                 (scourier2, sj_idx, sts2)]:
                    best_dict = courier_best.get(courier_id, {})
                    entry = best_dict.get(merged_key)
                    if entry is None:
                        continue
                    cidx, nc = entry
                    if candidates[cidx][0] == cur_ts:
                        continue
                    extra = candidates[cidx][4] - 2
                    benefit = old_total - nc + penalty * extra
                    if benefit > best_benefit:
                        best_benefit = benefit
                        other_courier = scourier2 if courier_id == scourier else scourier
                        best_action = ('swap', pos, cidx, courier_id, other_courier)

            for mj in range(nm):
                mj_idx, mts, mcourier = multis[mj]
                mtasks_list = sorted(mts.split(','))
                merged_list = sorted(mtasks_list + [sts])
                merged_key = ','.join(merged_list)
                merged_size = len(merged_list)
                old_total = scost + cost_lookup[(mts, mcourier)]

                best_dict = courier_best.get(mcourier, {})
                entry = best_dict.get(merged_key)
                if entry is not None:
                    cidx, nc = entry
                    if candidates[cidx][0] != mts:
                        extra = candidates[cidx][4] - merged_size
                        benefit = old_total - nc + penalty * extra
                        if benefit > best_benefit:
                            best_benefit = benefit
                            best_action = ('swap_and_remove', mj_idx, cidx,
                                           mcourier, scourier)

                best_dict_s = courier_best.get(scourier, {})
                entry_s = best_dict_s.get(merged_key)
                if entry_s is not None:
                    cidx, nc = entry_s
                    if candidates[cidx][0] != sts:
                        extra = candidates[cidx][4] - merged_size
                        benefit = old_total - nc + penalty * extra
                        if benefit > best_benefit:
                            best_benefit = benefit
                            best_action = ('swap_and_remove', si_idx, cidx,
                                           scourier, mcourier)

        if best_action is None:
            break

        _, keeper_pos, cidx, keeper_courier, removed_courier = best_action
        alt_ts = candidates[cidx][0]
        current[keeper_pos] = (alt_ts, [keeper_courier])

        rm_idx = None
        for i in range(len(current)):
            if current[i][1][0] == removed_courier:
                rm_idx = i
                break

        if rm_idx is not None and rm_idx != keeper_pos:
            current.pop(rm_idx)
            improved = True

    return current