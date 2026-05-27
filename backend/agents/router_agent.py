import json
from backend.minimax_client import minimax_chat

SPATIAL_NODES = [
    {"id": "Node-0x1A", "capacity": 600, "current_load": 0},
    {"id": "Node-0x2B", "capacity": 500, "current_load": 0},
    {"id": "Node-0x3C", "capacity": 700, "current_load": 0},
    {"id": "Node-0x4A", "capacity": 400, "current_load": 0},
    {"id": "Node-0x5F", "capacity": 550, "current_load": 0},
]


class AgentLog:
    def __init__(self):
        self.entries = []

    def warn(self, agent, message):
        self.entries.append(f"[{agent}][WARN] {message}")

    def info(self, agent, message):
        self.entries.append(f"[{agent}][INFO] {message}")

    def to_list(self):
        return list(self.entries)


class RouterAgent:
    def __init__(self, log):
        self.log = log
        self.name = "Router-Agent"

    def _get_node_loads(self, allocation, nodes):
        loads = {n["id"]: 0 for n in nodes}
        for info in allocation.values():
            if info["node"] in loads:
                loads[info["node"]] += info["load"]
        return loads

    def _greedy_pick(self, nodes, node_loads, load_increment):
        best_node = None
        best_remaining = -1
        for node in nodes:
            remaining = node["capacity"] - node_loads.get(node["id"], 0)
            if remaining >= load_increment and remaining > best_remaining:
                best_remaining = remaining
                best_node = node
        if best_node is None:
            best_node = min(nodes, key=lambda n: node_loads.get(n["id"], 0))
        return best_node

    def plan_routes(self, nodes, parts):
        self.log.info(self.name, "启动贪心路径规划引擎，分析空间节点拓扑...")
        allocation = {}
        total_weight = 0
        node_loads = {n["id"]: 0 for n in nodes}
        sorted_parts = sorted(parts, key=lambda p: p["weight"] * p["demand"], reverse=True)
        for part in sorted_parts:
            load_increment = part["weight"] * part["demand"]
            best_node = self._greedy_pick(nodes, node_loads, load_increment)
            allocation[part["part_id"]] = {
                "node": best_node["id"],
                "load": load_increment,
                "part_name": part["name"],
            }
            node_loads[best_node["id"]] += load_increment
            total_weight += load_increment
            remaining = best_node["capacity"] - node_loads[best_node["id"]]
            self.log.info(
                self.name,
                f"贪心分配 {part['name']}({part['part_id']}) → {best_node['id']}，负载 +{load_increment}，剩余容量 {remaining}",
            )
        self.log.info(
            self.name,
            f"贪心路径分配完成，共分配 {len(parts)} 类零件至 {len(set(a['node'] for a in allocation.values()))} 个节点，总负载 {total_weight}",
        )
        return allocation

    def replan_route(self, overloaded_node_id, allocation, nodes):
        self.log.warn(self.name, f"空间坐标节点 {overloaded_node_id} 超载，触发贪心反射重新规划...")
        node_loads = self._get_node_loads(allocation, nodes)
        overload_amount = node_loads[overloaded_node_id] - next(
            n["capacity"] for n in nodes if n["id"] == overloaded_node_id
        )
        overloaded_parts = [
            (part_id, info) for part_id, info in allocation.items()
            if info["node"] == overloaded_node_id
        ]
        if not overloaded_parts:
            self.log.info(self.name, f"节点 {overloaded_node_id} 无需迁移")
            return allocation
        overloaded_parts.sort(key=lambda x: x[1]["load"])
        alternative_nodes = [n for n in nodes if n["id"] != overloaded_node_id]
        if not alternative_nodes:
            self.log.warn(self.name, "无可用替代节点，保持当前分配")
            return allocation
        reallocated = 0
        migrated_load = 0
        for part_id, info in overloaded_parts:
            if migrated_load >= overload_amount:
                break
            best_node = self._greedy_pick(alternative_nodes, node_loads, info["load"])
            self.log.info(
                self.name,
                f"贪心迁移 {info['part_name']}({part_id}) 从 {overloaded_node_id} → {best_node['id']}（负载 {info['load']}）",
            )
            node_loads[overloaded_node_id] -= info["load"]
            info["node"] = best_node["id"]
            node_loads[best_node["id"]] += info["load"]
            migrated_load += info["load"]
            reallocated += 1
        self.log.info(
            self.name,
            f"贪心反射重规划完成，迁移 {reallocated} 项（释放 {migrated_load} 负载），绕过超载节点 {overloaded_node_id}",
        )
        return allocation
