class InventoryAgent:
    def __init__(self, log):
        self.log = log
        self.name = "Inventory-Agent"

    def check_inventory(self, parts):
        self.log.info(self.name, "启动库存核对流程，扫描零件库存数据...")
        shortage_count = 0
        inventory_status = {}
        for part in parts:
            stock = int(part["demand"] * part.get("stock_ratio", 0.9))
            deficit = max(0, part["demand"] - stock)
            shortage_count += deficit
            inventory_status[part["part_id"]] = {
                "part_name": part["name"],
                "demand": part["demand"],
                "stock": stock,
                "deficit": deficit,
            }
            if deficit > 0:
                self.log.warn(
                    self.name,
                    f"{part['name']}({part['part_id']}) 库存不足：需求 {part['demand']}，库存 {stock}，缺口 {deficit}",
                )
            else:
                self.log.info(
                    self.name,
                    f"{part['name']}({part['part_id']}) 库存充足：需求 {part['demand']}，库存 {stock}",
                )
        self.log.info(self.name, f"库存核对完成，总缺口零件数 {shortage_count}")
        return {"shortage_count": shortage_count, "status": inventory_status}
