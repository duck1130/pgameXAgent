"""
🎮 Survival Realm - 物品系統
處理所有物品相關的邏輯，包括物品定義、物品欄管理等

作者: 硬漢貓咪開發團隊 🐱
日期: 2025-07-30
版本: 3.1.0 (重構版本)
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
from ..core.config import ItemType


@dataclass
class Item:
    """遊戲物品類 - 定義單個物品的屬性"""

    id: str  # 物品唯一標識符
    name: str  # 物品顯示名稱
    item_type: ItemType  # 物品類型
    stack_size: int  # 最大堆疊數量
    description: str = ""  # 物品描述

    def can_stack_with(self, other: "Item") -> bool:
        """
        檢查是否可以與另一個物品疊加

        Args:
            other (Item): 另一個物品

        Returns:
            bool: 是否可以疊加
        """
        return self.id == other.id and self.stack_size > 1


@dataclass
class ItemStack:
    """物品堆疊類 - 管理物品的數量"""

    item: Item  # 物品對象
    quantity: int = 1  # 當前數量

    def can_add(self, amount: int) -> bool:
        """
        檢查是否可以添加指定數量

        Args:
            amount (int): 要添加的數量

        Returns:
            bool: 是否可以添加
        """
        return self.quantity + amount <= self.item.stack_size

    def add(self, amount: int) -> int:
        """
        添加物品到堆疊

        Args:
            amount (int): 要添加的數量

        Returns:
            int: 實際添加的數量
        """
        max_add = min(amount, self.item.stack_size - self.quantity)
        self.quantity += max_add
        return max_add

    def remove(self, amount: int) -> int:
        """
        從堆疊移除物品

        Args:
            amount (int): 要移除的數量

        Returns:
            int: 實際移除的數量
        """
        actual_remove = min(amount, self.quantity)
        self.quantity -= actual_remove
        return actual_remove

    def is_empty(self) -> bool:
        """檢查堆疊是否為空"""
        return self.quantity <= 0


class Inventory:
    """物品欄系統 - 管理玩家的物品存儲"""

    def __init__(self, size: int = 20):
        """
        初始化物品欄

        Args:
            size (int): 物品欄大小
        """
        self.size = size
        self.slots: List[Optional[ItemStack]] = [None] * size

    def add_item(self, item: Item, quantity: int = 1) -> int:
        """
        添加物品到物品欄

        Args:
            item (Item): 要添加的物品
            quantity (int): 數量

        Returns:
            int: 實際添加的數量
        """
        remaining = quantity

        # 步驟1: 先嘗試疊加到現有物品堆
        for slot in self.slots:
            if slot and slot.item.can_stack_with(item) and remaining > 0:
                added = slot.add(remaining)
                remaining -= added

        # 步驟2: 如果還有剩餘，尋找空格放置
        for i, slot in enumerate(self.slots):
            if slot is None and remaining > 0:
                add_amount = min(remaining, item.stack_size)
                self.slots[i] = ItemStack(item, add_amount)
                remaining -= add_amount

        return quantity - remaining

    def remove_item(self, item_id: str, quantity: int = 1) -> int:
        """
        從物品欄移除物品

        Args:
            item_id (str): 物品ID
            quantity (int): 要移除的數量

        Returns:
            int: 實際移除的數量
        """
        removed = 0

        for i, slot in enumerate(self.slots):
            if slot and slot.item.id == item_id and removed < quantity:
                need_remove = quantity - removed
                actual_remove = slot.remove(need_remove)
                removed += actual_remove

                # 如果物品堆空了，清空槽位
                if slot.is_empty():
                    self.slots[i] = None

        return removed

    def has_item(self, item_id: str, quantity: int = 1) -> bool:
        """
        檢查是否有足夠的物品

        Args:
            item_id (str): 物品ID
            quantity (int): 需要的數量

        Returns:
            bool: 是否有足夠數量
        """
        total = self.get_item_count(item_id)
        return total >= quantity

    def get_item_count(self, item_id: str) -> int:
        """
        獲取指定物品的總數量

        Args:
            item_id (str): 物品ID

        Returns:
            int: 物品總數量
        """
        return sum(
            slot.quantity for slot in self.slots if slot and slot.item.id == item_id
        )

    def get_empty_slots(self) -> int:
        """獲取空槽位數量"""
        return sum(1 for slot in self.slots if slot is None)

    def is_full(self) -> bool:
        """檢查物品欄是否已滿"""
        return self.get_empty_slots() == 0

    def get_item_by_slot(self, slot_index: int) -> Optional[ItemStack]:
        """
        根據槽位索引獲取物品

        Args:
            slot_index (int): 槽位索引

        Returns:
            Optional[ItemStack]: 物品堆疊或None
        """
        if 0 <= slot_index < self.size:
            return self.slots[slot_index]
        return None

    def clear_slot(self, slot_index: int) -> bool:
        """
        清空指定槽位

        Args:
            slot_index (int): 槽位索引

        Returns:
            bool: 是否成功清空
        """
        if 0 <= slot_index < self.size:
            self.slots[slot_index] = None
            return True
        return False

    def get_items_by_type(self, item_type: ItemType) -> List[Tuple[int, ItemStack]]:
        """
        獲取指定類型的所有物品

        Args:
            item_type (ItemType): 物品類型

        Returns:
            List[Tuple[int, ItemStack]]: (槽位索引, 物品堆疊) 列表
        """
        result = []
        for i, slot in enumerate(self.slots):
            if slot and slot.item.item_type == item_type:
                result.append((i, slot))
        return result


class ItemDatabase:
    """物品資料庫 - 管理所有遊戲物品的定義"""

    def __init__(self):
        """初始化物品資料庫"""
        self._items: Dict[str, Item] = {}
        self._initialize_items()

    def _initialize_items(self) -> None:
        """初始化所有遊戲物品"""

        # ====== 基礎資源 ======
        self._add_item(
            Item("wood", "木材", ItemType.RESOURCE, 64, "用於建造的基礎材料，可以燃燒")
        )

        self._add_item(Item("stone", "石頭", ItemType.RESOURCE, 64, "堅固的建築材料"))

        # ====== 食物和消耗品 ======
        self._add_item(
            Item("food", "食物", ItemType.CONSUMABLE, 32, "恢復飢餓值的基本食物")
        )

        self._add_item(
            Item("berry", "漿果", ItemType.CONSUMABLE, 16, "野生漿果，恢復少量飢餓值")
        )

        self._add_item(
            Item(
                "mushroom",
                "蘑菇",
                ItemType.CONSUMABLE,
                16,
                "野生蘑菇，恢復飢餓值但可能有副作用",
            )
        )

        # ====== 礦物資源 ======
        self._add_item(
            Item("iron_ore", "鐵礦", ItemType.RESOURCE, 32, "可以燒製成鐵錠的礦物")
        )

        self._add_item(
            Item("coal", "煤炭", ItemType.RESOURCE, 32, "優質燃料，燃燒效率高")
        )

        self._add_item(
            Item(
                "iron_ingot",
                "鐵錠",
                ItemType.RESOURCE,
                16,
                "燒製後的鐵，用於製作高級物品",
            )
        )

        # ====== 貴重物品 ======
        self._add_item(
            Item("treasure", "寶物", ItemType.VALUABLE, 1, "珍貴的寶物，價值不菲")
        )

        self._add_item(
            Item(
                "rare_gem", "稀有寶石", ItemType.VALUABLE, 1, "極其珍貴的寶石，閃閃發光"
            )
        )

        # ====== 工具 ======
        self._add_item(
            Item("axe", "斧頭", ItemType.TOOL, 1, "砍樹專用工具，大幅提升砍伐效率")
        )

        self._add_item(
            Item(
                "pickaxe",
                "稿子",
                ItemType.TOOL,
                1,
                "挖掘專用工具，提升挖掘效率並能獲得礦物",
            )
        )

        self._add_item(
            Item("bucket", "木桶", ItemType.TOOL, 1, "用於取水的容器，提升取水效率")
        )

        # ====== 武器裝備 ======
        self._add_item(
            Item(
                "iron_sword", "鐵劍", ItemType.EQUIPMENT, 1, "銳利的鐵製劍，增加戰鬥力"
            )
        )

        self._add_item(
            Item(
                "iron_armor", "鐵甲", ItemType.EQUIPMENT, 1, "堅固的鐵製護甲，提供防護"
            )
        )

        # ====== 建築物 ======
        self._add_item(
            Item("workbench", "工作臺", ItemType.BUILDING, 1, "製作工具的工作台")
        )

        self._add_item(Item("furnace", "熔爐", ItemType.BUILDING, 1, "燒製礦物的設備"))

    def _add_item(self, item: Item) -> None:
        """添加物品到資料庫"""
        self._items[item.id] = item

    def get_item(self, item_id: str) -> Optional[Item]:
        """
        根據ID獲取物品

        Args:
            item_id (str): 物品ID

        Returns:
            Optional[Item]: 物品對象或None
        """
        return self._items.get(item_id)

    def get_all_items(self) -> Dict[str, Item]:
        """獲取所有物品"""
        return self._items.copy()

    def get_items_by_type(self, item_type: ItemType) -> Dict[str, Item]:
        """
        獲取指定類型的所有物品

        Args:
            item_type (ItemType): 物品類型

        Returns:
            Dict[str, Item]: 物品字典
        """
        return {
            item_id: item
            for item_id, item in self._items.items()
            if item.item_type == item_type
        }

    def item_exists(self, item_id: str) -> bool:
        """檢查物品是否存在"""
        return item_id in self._items


# 全域物品資料庫實例
item_database = ItemDatabase()
