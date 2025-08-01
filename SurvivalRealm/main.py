"""
Survival Realm - 主遊戲程式
2D RPG 生存遊戲 - 重構版本

作者: 開發團隊
日期: 2025-07-30
版本: 3.1.0 (重構版本)

好了好了，遊戲程式量太大被拆分重構了！
雖然本大爺很不想承認，但這次重構確實讓程式碼更乾淨了... (ˋ・ω・ˊ)
"""

import pygame
import sys
import time
from typing import List, Tuple, Optional

# 導入遊戲模組
from src.core.config import WINDOW_CONFIG, COLORS, GameState, UI_CONFIG, CAVE_CONFIG
from src.systems.inventory import item_database


class Game:
    """主遊戲類 - 遊戲核心邏輯管理"""

    def __init__(self):
        """初始化遊戲"""
        print("正在初始化 Survival Realm...")

        # 初始化 pygame
        pygame.init()
        pygame.mixer.init()

        # 遊戲基本設定
        self.running = True
        self._state = GameState.PLAYING  # 使用私有變量
        self.clock = pygame.time.Clock()

        # 創建遊戲視窗
        # 初始化全螢幕模式
        if WINDOW_CONFIG.get("fullscreen", False):
            self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
            # 更新實際的螢幕尺寸
            WINDOW_CONFIG["width"] = self.screen.get_width()
            WINDOW_CONFIG["height"] = self.screen.get_height()
            print(f"全螢幕模式啟動: {WINDOW_CONFIG['width']}x{WINDOW_CONFIG['height']}")
        else:
            self.screen = pygame.display.set_mode(
                (WINDOW_CONFIG["width"], WINDOW_CONFIG["height"])
            )
        pygame.display.set_caption(WINDOW_CONFIG["title"])

        # 初始化遊戲系統
        from src.world.world_manager import WorldManager
        from src.systems.time_manager import TimeManager
        from src.systems.music_manager import MusicManager
        from src.systems.sound_manager import sound_manager
        from src.world.cave_system import cave_system
        from src.systems.camera import camera  # 導入相機系統

        self.world_manager = WorldManager()
        print("世界: 世界管理器初始化完成")

        self.music_manager = MusicManager()
        print("音樂: 音樂管理器初始化完成！")

        # 音效系統
        self.sound_manager = sound_manager
        print("🔊 音效管理器初始化完成！腳步聲系統就位")

        # 洞穴系統
        self.cave_system = cave_system
        self.pending_cave_entry = None  # 待進入的洞穴信息
        print("洞穴探險系統初始化完成！")

        # 相機系統
        self.camera = camera
        print("相機系統初始化完成！玩家將固定在螢幕中心")

        # 初始化 UI 系統
        from src.ui.user_interface import UI

        self.ui = UI()
        print("UI系統初始化完成！")

        # 初始化玩家
        from src.entities.player import Player

        # 玩家在相機系統中的世界座標（可以任意設定）
        spawn_x = 0  # 世界中心
        spawn_y = 0  # 世界中心
        self.player = Player(spawn_x, spawn_y)

        # 🐱 硬漢貓咪調試：給玩家一些測試材料
        from src.systems.inventory import item_database

        # 給玩家初始資源（調試用）
        wood_item = item_database.get_item("wood")
        stone_item = item_database.get_item("stone")
        coal_item = item_database.get_item("coal")  # 新增煤炭
        if wood_item:
            self.player.inventory.add_item(wood_item, 10)  # 給10個木材
            print(f"調試: 調試：給玩家添加了 10 個木材")
        if stone_item:
            self.player.inventory.add_item(stone_item, 10)  # 給10個石頭
            print(f"調試: 調試：給玩家添加了 10 個石頭")
        if coal_item:
            self.player.inventory.add_item(coal_item, 5)  # 給5個煤炭用於製作火把
            print(f"調試: 調試：給玩家添加了 5 個煤炭")

        # 初始化時間管理器
        self.time_manager = TimeManager()

        # 生成初始世界
        self.world_manager.generate_world()

        # 初始化背景音樂
        self.music_manager.load_music("main_theme")
        self.music_manager.play_music("main_theme")

        # 訊息系統
        self.messages: List[Tuple[str, float]] = []
        self.message_duration = 5.0  # 訊息顯示時間（秒）

        print("遊戲初始化完成！")
        self._print_controls()

    @property
    def state(self):
        """取得遊戲狀態"""
        return self._state

    @state.setter
    def state(self, new_state):
        """設定遊戲狀態（帶調試）"""
        if self._state != new_state:
            print(f"狀態變化: {self._state} -> {new_state}")
            import traceback

            print(f"📍 調用堆疊: {traceback.format_stack()[-2].strip()}")
        self._state = new_state

    def _print_controls(self) -> None:
        """打印控制說明"""
        print("操作說明:")
        print("   WASD - 移動角色")
        print("   E - 與物件互動")
        print("   Enter - 進入/退出洞穴")
        print("   L - 使用照明工具（洞穴內）")
        print("   F - 消耗食物")
        print("   I - 開啟/關閉物品欄")
        print(
            "   C - 製作介面 (1=斧頭 2=稿子 3=水桶 4=火把 5=工作台 6=熔爐 7=鐵劍 8=鐵甲)"
        )
        print("   T - 燒製介面 (需靠近熔爐，1=燒製鐵錠)")
        print("   P - 放置建築物 (工作台/熔爐)")
        print("   M - 切換背景音樂")
        print("   + - 增加音量")
        print("   - - 減少音量")
        print(
            "   1-8 - 裝備物品 (1=斧頭 2=稿子 3=水桶 4=火把 5-6=建築物 7=鐵劍 8=鐵甲)"
        )
        print("   ESC - 暫停/繼續遊戲")
        print("   Q - 退出遊戲")
        print("提示: 製作和裝備使用統一的 1-8 按鍵映射！")
        print("洞穴探險: 找到洞穴後需要火把才能進入，小心黑暗和怪物！")
        print("河流: 稀有河流: 河流不會重新生成，珍惜每一個水源！")

    def handle_events(self) -> None:
        """處理遊戲事件"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            elif event.type == pygame.KEYDOWN:
                print(
                    f"載入: 事件前狀態: {self.state}, 製作模式: {self.player.crafting_mode}"
                )
                self._handle_keydown(event.key)
                print(
                    f"載入: 事件後狀態: {self.state}, 製作模式: {self.player.crafting_mode}"
                )

            elif event.type == pygame.MOUSEWHEEL:
                # 處理滾輪事件（在製作界面中）
                if self.state == GameState.CRAFTING:
                    self.ui.crafting_scroll_offset -= (
                        event.y * 20
                    )  # 向上滾動減少偏移，增加滾動速度

    def _handle_keydown(self, key: int) -> None:
        """處理按鍵按下事件"""
        # ESC 鍵 - 狀態切換
        if key == pygame.K_ESCAPE:
            print(f"ESC鍵被按下，當前狀態: {self.state}")
            old_state = self.state
            if self.state == GameState.PLAYING:
                self.state = GameState.PAUSED
                print(f"切換到暫停狀態")
            elif self.state in [
                GameState.PAUSED,
                GameState.INVENTORY,
                GameState.CRAFTING,
                GameState.SMELTING,
            ]:
                self.state = GameState.PLAYING
                self.player.crafting_mode = False
                self.player.smelting_mode = False
                print(f"重設所有狀態，回到遊戲狀態")

            # 更新音樂狀態
            self._update_music_for_state_change(old_state, self.state)

        # Q 鍵 - 快速退出
        elif key == pygame.K_q:
            self.running = False

        # 遊戲進行中的按鍵 (包括製作和燒製狀態)
        elif self.state in [GameState.PLAYING, GameState.CRAFTING, GameState.SMELTING]:
            self._handle_gameplay_keys(key)

    def _handle_gameplay_keys(self, key: int) -> None:
        """處理遊戲進行中的按鍵"""
        if key == pygame.K_e:
            # 與世界互動 (僅在遊戲狀態下)
            if self.state == GameState.PLAYING:
                if self.cave_system.in_cave:
                    # 在洞穴中，與洞穴物件互動
                    cave_objects = self.cave_system.get_cave_objects()
                    player_center_x = self.player.x + self.player.width // 2
                    player_center_y = self.player.y + self.player.height // 2

                    for obj in cave_objects:
                        if obj.is_near(
                            player_center_x,
                            player_center_y,
                            self.player.interaction_range,
                        ):
                            result = obj.interact(self.player)
                            if result:
                                self.add_message(result["message"])

                                # 處理Boss戰結果
                                if result.get("boss_defeated"):
                                    depth = result.get("depth", 1)
                                    self.cave_system.handle_boss_death(depth)
                                    self.add_message(
                                        f"獲得了第{depth + 1}層的入場鑰匙！"
                                    )

                                # 處理物品掉落
                                if "items" in result:
                                    for item_id, amount in result["items"]:
                                        # 特殊處理深度鑰匙
                                        if item_id == "depth_key":
                                            # 不添加到背包，直接解鎖權限
                                            continue

                                        item = item_database.get_item(item_id)
                                        if item:
                                            self.player.inventory.add_item(item, amount)
                            break
                else:
                    # 在地表，正常互動
                    result = self.player.interact_with_world(self.world_manager)
                    if result:
                        # 檢查是否是洞穴入口
                        if isinstance(result, dict) and result.get("cave_entry"):
                            self._handle_cave_entry_result(result)
                        else:
                            self.add_message(result)

        elif key == pygame.K_RETURN:  # Enter鍵
            # 進入洞穴
            if self.state == GameState.PLAYING and self.pending_cave_entry:
                self.enter_cave()
            # 退出洞穴
            elif self.cave_system.in_cave:
                self.exit_cave()

        elif key == pygame.K_f:
            # 消耗食物 (僅在遊戲狀態下)
            if self.state == GameState.PLAYING:
                # 獲取消耗前的飢餓值
                old_hunger = self.player.survival_stats.hunger

                if self.player.consume_food():
                    new_hunger = self.player.survival_stats.hunger
                    hunger_gained = new_hunger - old_hunger
                    self.add_message(
                        f"消耗食物！飢餓值恢復了 {hunger_gained:.1f} 點 (當前: {new_hunger:.1f}/100)"
                    )
                else:
                    self.add_message("沒有食物可以消耗！需要收集漿果或其他食物")

        elif key == pygame.K_l:  # L鍵 - 使用照明工具
            if self.cave_system.in_cave:
                if self.cave_system.use_torch(self.player):
                    self.add_message("點燃了火把，照亮了周圍！")
                elif self.cave_system.use_cave_lamp(self.player):
                    self.add_message("開啟了洞穴燈，光明持續更久！")
                else:
                    self.add_message("沒有照明工具！黑暗正在侵蝕你...")

        elif key == pygame.K_i:
            # 切換物品欄 (僅在遊戲狀態下)
            if self.state == GameState.PLAYING:
                self.state = (
                    GameState.INVENTORY
                    if self.state != GameState.INVENTORY
                    else GameState.PLAYING
                )

        elif key == pygame.K_c:
            # 製作介面 (僅在遊戲狀態下才能切換)
            if self.state == GameState.PLAYING:
                print(
                    f"C鍵被按下，當前狀態: {self.state}, 製作模式: {self.player.crafting_mode}"
                )

                # 顯示玩家當前材料狀況
                wood_count = self.player.inventory.get_item_count("wood")
                stone_count = self.player.inventory.get_item_count("stone")
                empty_slots = self.player.inventory.get_empty_slots()
                print(
                    f"玩家材料狀況：木材={wood_count}, 石頭={stone_count}, 空槽位={empty_slots}"
                )

                # 顯示製作模式切換前的狀態
                print(
                    f"載入: 製作模式切換前: crafting_mode={self.player.crafting_mode}, state={self.state}"
                )

                self.player.crafting_mode = not self.player.crafting_mode
                self.player.smelting_mode = False

                print(
                    f"載入: 製作模式切換後: crafting_mode={self.player.crafting_mode}"
                )

                if self.player.crafting_mode:
                    self.state = GameState.CRAFTING
                    print(
                        f"進入製作模式！新狀態: {self.state}, 製作模式: {self.player.crafting_mode}"
                    )
                    self.add_message("進入製作模式！按 1-7 製作物品")
                else:
                    self.state = GameState.PLAYING
                    print(
                        f"退出製作模式！新狀態: {self.state}, 製作模式: {self.player.crafting_mode}"
                    )
                    self.add_message("退出製作模式")

        elif key == pygame.K_t:
            # 燒製介面 (T key - smelTing) (僅在遊戲狀態下才能切換)
            if self.state == GameState.PLAYING:
                if not self._is_near_furnace():
                    self.add_message("需要靠近熔爐才能進入燒製模式！")
                    return

                self.player.smelting_mode = not self.player.smelting_mode
                self.player.crafting_mode = False
                if self.player.smelting_mode:
                    self.state = GameState.SMELTING
                    self.add_message("進入燒製模式！按 1 燒製鐵錠")
                else:
                    self.state = GameState.PLAYING
                    self.add_message("退出燒製模式")

        elif key == pygame.K_p:
            # 放置建築物模式 (僅在遊戲狀態下)
            if self.state == GameState.PLAYING:
                self._handle_place_building()

        elif key == pygame.K_m:
            # 切換音樂播放 (任何遊戲狀態都可以)
            is_playing = self.music_manager.toggle_music()
            status = "開啟" if is_playing else "關閉"
            self.add_message(f"音樂: 背景音樂已{status}")

        elif key == pygame.K_PLUS or key == pygame.K_EQUALS:
            # 增加音量 (任何遊戲狀態都可以)
            current_volume = self.music_manager.volume
            new_volume = min(1.0, current_volume + 0.1)
            self.music_manager.set_volume(new_volume)
            self.add_message(f"🔊 音量: {int(new_volume * 100)}%")

        elif key == pygame.K_MINUS:
            # 減少音量 (任何遊戲狀態都可以)
            current_volume = self.music_manager.volume
            new_volume = max(0.0, current_volume - 0.1)
            self.music_manager.set_volume(new_volume)
            self.add_message(f"🔉 音量: {int(new_volume * 100)}%")

        # 數字鍵操作 (在所有允許的遊戲狀態下都可以)
        elif pygame.K_1 <= key <= pygame.K_8:
            number = key - pygame.K_1 + 1
            self._handle_number_key(number)

    def _handle_number_key(self, number: int) -> None:
        """處理數字鍵輸入"""
        print(f"調試：收到數字鍵 {number}，當前狀態: {self.state}")
        print(f"調試：玩家製作模式: {self.player.crafting_mode}")
        print(f"調試：玩家燒製模式: {self.player.smelting_mode}")
        print(f"調試：完整狀態檢查:")
        print(f"   - GameState == CRAFTING: {self.state == GameState.CRAFTING}")
        print(f"   - GameState == SMELTING: {self.state == GameState.SMELTING}")
        print(f"   - GameState == INVENTORY: {self.state == GameState.INVENTORY}")
        print(f"   - crafting_mode == True: {self.player.crafting_mode == True}")
        print(f"   - smelting_mode == True: {self.player.smelting_mode == True}")

        # 檢查雙重條件 - 製作模式
        if self.player.crafting_mode or self.state == GameState.CRAFTING:
            print(f"調試：進入製作條件分支，呼叫製作處理")
            self._handle_crafting(number)
        # 檢查雙重條件 - 燒製模式
        elif self.player.smelting_mode or self.state == GameState.SMELTING:
            print(f"調試：進入燒製條件分支，呼叫燒製處理")
            self._handle_smelting(number)
        # 物品欄狀態
        elif self.state == GameState.INVENTORY:
            print(f"🎒 調試：在物品欄狀態")
            # 在物品欄中，數字鍵可能有不同行為
        else:
            print(f"調試：在其他狀態 ({self.state})，嘗試裝備")
            self._handle_equipment(number)

    def _handle_crafting(self, number: int) -> None:
        """處理製作操作"""
        print(f"調試: 調試：進入製作處理，數字={number}")

        recipes = [
            "axe",
            "pickaxe",
            "bucket",
            "torch",
            "workbench",
            "furnace",
            "iron_sword",
            "iron_armor",
        ]

        print(f"📋 調試：可用配方 {len(recipes)} 個: {recipes}")

        if 1 <= number <= len(recipes):
            item_id = recipes[number - 1]
            print(f"調試：選中物品 {item_id} (索引 {number-1})")

            # 檢查玩家材料狀況
            if item_id == "workbench":
                wood_count = self.player.inventory.get_item_count("wood")
                print(f"🌳 調試：玩家當前木材數量: {wood_count} (需要4個)")
                print(f"調試：物品欄空槽位: {self.player.inventory.get_empty_slots()}")
                print(f"調試：物品欄已滿: {self.player.inventory.is_full()}")

            # 工作台和火把可以隨時製作（基礎製作）
            if item_id in ["workbench", "torch"]:
                print(f"調試：製作基礎物品 {item_id}，呼叫 _craft_item")
                message = self._craft_item(item_id)
                print(f"📝 調試：製作結果訊息: {message}")
                if message:
                    self.add_message(message)
                return

            # 其他物品需要靠近工作台才能製作（高級製作）
            if not self._is_near_workbench():
                print(f"調試：不在工作台附近，無法製作 {item_id}")
                self.add_message(f"製作 {item_id} 需要靠近工作台！")
                return

            print(f"🏭 調試：在工作台附近，可以製作 {item_id}")
            message = self._craft_item(item_id)
            print(f"📝 調試：製作結果訊息: {message}")
            if message:
                self.add_message(message)
        else:
            print(f"調試：數字 {number} 超出範圍 (1-{len(recipes)})")
            self.add_message(
                "請按 1-8：1=斧頭 2=稿子 3=水桶 4=火把 5=工作台 6=熔爐 7=鐵劍 8=鐵甲"
            )

    def _handle_smelting(self, number: int) -> None:
        """處理燒製操作"""
        # 檢查是否靠近熔爐
        if not self._is_near_furnace():
            self.add_message("需要靠近熔爐才能燒製！")
            return

        if number == 1:  # 只有鐵錠可以燒製
            message = self._smelt_item("iron_ingot")
            if message:
                self.add_message(message)

    def _handle_equipment(self, number: int) -> None:
        """處理裝備操作"""
        # 統一順序：工具、建築物、武器裝備
        equipment_items = [
            "axe",
            "pickaxe",
            "bucket",
            "torch",
            "workbench",
            "furnace",
            "iron_sword",
            "iron_armor",
        ]

        if 1 <= number <= len(equipment_items):
            item_id = equipment_items[number - 1]

            # 建築物不能裝備，只能放置
            if item_id in ["workbench", "furnace"]:
                self.add_message(f"{item_id} 是建築物，按 P 鍵放置！")
                return

            if self.player.inventory.has_item(item_id, 1):
                if self.player.equip_item(item_id):
                    item = item_database.get_item(item_id)
                    self.add_message(f"成功: 成功裝備了 {item.name}！")
            else:
                item = item_database.get_item(item_id)
                if item:
                    self.add_message(f"你沒有 {item.name}，需要先製作！")
        else:
            self.add_message(
                "請按 1-7：1=斧頭 2=稿子 3=水桶 4=工作台 5=熔爐 6=鐵劍 7=鐵甲"
            )

    def _craft_item(self, item_id: str) -> Optional[str]:
        """製作物品邏輯"""
        from src.core.config import ITEM_RECIPES

        if item_id not in ITEM_RECIPES:
            return "無法製作此物品"

        recipe = ITEM_RECIPES[item_id]
        item = item_database.get_item(item_id)

        if not item:
            return "物品不存在"

        # 檢查材料
        missing_materials = []
        for material, amount in recipe.items():
            if not self.player.inventory.has_item(material, amount):
                owned = self.player.inventory.get_item_count(material)
                missing_materials.append(f"{material} (需要{amount}，擁有{owned})")

        if missing_materials:
            return f"缺少材料: {', '.join(missing_materials)}"

        # 檢查物品欄空間
        if self.player.inventory.is_full():
            empty_slots = self.player.inventory.get_empty_slots()
            if empty_slots == 0:
                return "物品欄已滿，無法製作！請先清理物品欄"

        # 消耗材料
        consumed_materials = []
        for material, amount in recipe.items():
            removed = self.player.inventory.remove_item(material, amount)
            consumed_materials.append(f"{material} x{removed}")

        # 添加製作出的物品
        added = self.player.inventory.add_item(item, 1)
        if added > 0:
            # 顯示詳細的製作成功信息
            materials_used = ", ".join(consumed_materials)
            return f"成功: 製作成功！獲得 [{item.name}] \n消耗材料: {materials_used}"
        else:
            # 如果添加失敗，恢復材料
            for material, amount in recipe.items():
                mat_item = item_database.get_item(material)
                if mat_item:
                    self.player.inventory.add_item(mat_item, amount)
            return "物品欄已滿，製作失敗！材料已退還"

        return "製作失敗，未知錯誤"

    def _smelt_item(self, item_id: str) -> Optional[str]:
        """燒製物品邏輯"""
        if item_id == "iron_ingot":
            if not self.player.inventory.has_item("iron_ore", 1):
                return "缺少鐵礦"

            has_fuel = self.player.inventory.has_item(
                "coal", 1
            ) or self.player.inventory.has_item("wood", 1)
            if not has_fuel:
                return "缺少燃料(煤炭或木材)"

            # 消耗材料和燃料
            self.player.inventory.remove_item("iron_ore", 1)
            if self.player.inventory.has_item("coal", 1):
                self.player.inventory.remove_item("coal", 1)
            else:
                self.player.inventory.remove_item("wood", 1)

            # 添加鐵錠
            item = item_database.get_item("iron_ingot")
            if item:
                added = self.player.inventory.add_item(item, 1)
                if added > 0:
                    return "成功燒製了鐵錠！已添加到物品欄"
                else:
                    return "物品欄已滿，無法燒製"

        return "無法燒製此物品"

    def _is_near_workbench(self) -> bool:
        """檢查是否靠近工作台"""
        from src.world.world_objects import Workbench

        center_x = self.player.x + self.player.width // 2
        center_y = self.player.y + self.player.height // 2

        # 只檢查世界中的工作台
        workbenches = self.world_manager.get_objects_by_type(Workbench)

        for workbench in workbenches:
            distance = (
                (workbench.x - center_x) ** 2 + (workbench.y - center_y) ** 2
            ) ** 0.5
            if distance <= 80:  # 80像素範圍內
                return True

        return False

    def _is_near_furnace(self) -> bool:
        """檢查是否靠近熔爐"""
        from src.world.world_objects import Furnace

        center_x = self.player.x + self.player.width // 2
        center_y = self.player.y + self.player.height // 2

        # 只檢查世界中的熔爐
        furnaces = self.world_manager.get_objects_by_type(Furnace)
        for furnace in furnaces:
            distance = (
                (furnace.x - center_x) ** 2 + (furnace.y - center_y) ** 2
            ) ** 0.5
            if distance <= 80:  # 80像素範圍內
                return True

        return False

    def _handle_place_building(self) -> None:
        """處理放置建築物"""
        # 檢查玩家是否有工作台或熔爐
        if self.player.inventory.has_item("workbench", 1):
            message = self.player.place_building("workbench", self.world_manager)
            self.add_message(message)
        elif self.player.inventory.has_item("furnace", 1):
            message = self.player.place_building("furnace", self.world_manager)
            self.add_message(message)
        else:
            self.add_message("沒有可放置的建築物")

    def add_message(self, message: str) -> None:
        """
        添加遊戲訊息

        Args:
            message (str): 要顯示的訊息
        """
        current_time = time.time()
        self.messages.append((message, current_time))

        # 限制訊息數量
        max_messages = UI_CONFIG["max_messages"]
        if len(self.messages) > max_messages:
            self.messages.pop(0)

    def update(self) -> None:
        """更新遊戲邏輯"""
        if self.state not in [
            GameState.PLAYING,
            GameState.CRAFTING,
            GameState.SMELTING,
        ]:
            return

        # 計算幀時間
        delta_time = self.clock.get_time() / 1000.0

        # 處理玩家輸入（只在遊戲進行時）
        if self.state == GameState.PLAYING:
            keys = pygame.key.get_pressed()
            self.player.handle_input(keys)

        # 更新各系統
        self.player.update(
            delta_time,
            WINDOW_CONFIG["width"],
            WINDOW_CONFIG["height"],
            self.cave_system,
        )

        # 更新相機位置跟隨玩家
        player_center_x, player_center_y = self.player.get_world_center()
        self.camera.update(player_center_x, player_center_y, delta_time)

        # 更新世界管理器（獲取消息）
        player_center_x = self.player.x + self.player.width // 2
        player_center_y = self.player.y + self.player.height // 2
        world_messages = self.world_manager.update(
            delta_time,
            self.player.has_moved_this_turn,
            player_center_x,
            player_center_y,
            self.time_manager,
        )

        # 添加世界消息
        for message in world_messages:
            self.add_message(message)

        # 處理怪物主動攻擊
        self._handle_monster_attacks()

        # 更新洞穴系統（如果在洞穴中）
        if self.cave_system.in_cave:
            cave_messages = self.cave_system.update(delta_time, self.player)
            for message in cave_messages:
                self.add_message(message)

        self.time_manager.update(delta_time)

        # 清理過期訊息
        self._cleanup_messages()

        # 根據時間更新音樂
        self.music_manager.update_music_for_state(
            self.state, self.time_manager.get_time_of_day()
        )

        # 檢查遊戲結束條件
        if not self.player.is_alive():
            self.state = GameState.GAME_OVER

    def _handle_monster_attacks(self) -> None:
        """處理怪物主動攻擊"""
        from src.world.world_objects import Monster

        for obj in self.world_manager.objects:
            if isinstance(obj, Monster) and obj.active:
                if obj.state == "attacking" and obj._can_attack():
                    # 檢查距離
                    player_center_x = self.player.x + self.player.width // 2
                    player_center_y = self.player.y + self.player.height // 2
                    monster_center_x = obj.x + obj.width // 2
                    monster_center_y = obj.y + obj.height // 2

                    distance = (
                        (player_center_x - monster_center_x) ** 2
                        + (player_center_y - monster_center_y) ** 2
                    ) ** 0.5

                    if distance <= obj.attack_range:
                        attack_result = obj._perform_attack()
                        if attack_result and attack_result.get("monster_attack"):
                            damage = attack_result.get("damage", 0)
                            actual_damage = self.player.take_damage(damage)
                            self.add_message(
                                f"怪物攻擊了你！受到 {actual_damage} 點傷害"
                            )

    def _handle_cave_entry_result(self, result: dict) -> None:
        """處理洞穴互動結果"""
        if result.get("cave_entry"):
            self.pending_cave_entry = result
            self.add_message(result["message"])
        else:
            self.add_message(result["message"])

    def enter_cave(self) -> None:
        """進入洞穴 - 支援深度選擇和鑰匙檢查"""
        if self.pending_cave_entry:
            base_depth = self.pending_cave_entry.get("cave_depth", 1)

            # 讓玩家選擇要進入的深度
            max_depth = min(
                self.cave_system.max_unlocked_depth, CAVE_CONFIG["max_depth"]
            )

            # 簡化版本：直接進入最深可到達的層數
            # 未來可以加入UI讓玩家選擇
            depth = max_depth

            # 檢查鑰匙權限
            if depth > self.cave_system.max_unlocked_depth:
                self.add_message(f"你需要第{depth-1}層的鑰匙才能進入第{depth}層！")
                self.pending_cave_entry = None
                return

            # 使用火把或洞穴燈
            if self.cave_system.use_torch(self.player):
                self.add_message("點燃火把，準備探險！")
            elif self.cave_system.use_cave_lamp(self.player):
                self.add_message("開啟洞穴燈，準備深入探險！")
            else:
                self.add_message("沒有照明工具！黑暗中會很危險！")

            # 進入洞穴
            room = self.cave_system.enter_cave(depth)
            if room:
                boss_info = "有強大的Boss守護" if room.boss else "沒有Boss"
                self.add_message(f"進入了第 {depth} 層洞穴！({boss_info})")
                self.add_message(f"此層充滿了大量怪物和寶藏！小心探索！")
            else:
                self.add_message("無法進入此層洞穴！")

            self.pending_cave_entry = None

    def exit_cave(self) -> None:
        """退出洞穴"""
        if self.cave_system.in_cave:
            self.cave_system.exit_cave()
            self.add_message("回到了地表，陽光真好！")

    def _cleanup_messages(self) -> None:
        """清理過期的訊息"""
        current_time = time.time()
        self.messages = [
            (msg, timestamp)
            for msg, timestamp in self.messages
            if current_time - timestamp < self.message_duration
        ]

    def _update_music_for_state_change(
        self, old_state: GameState, new_state: GameState
    ) -> None:
        """
        當遊戲狀態改變時更新音樂

        Args:
            old_state (GameState): 舊狀態
            new_state (GameState): 新狀態
        """
        if new_state == GameState.PAUSED:
            self.music_manager.pause_music()
        elif old_state == GameState.PAUSED and new_state == GameState.PLAYING:
            self.music_manager.unpause_music()
        elif new_state == GameState.GAME_OVER:
            self.music_manager.stop_music(fade_out=True)

    def draw(self) -> None:
        """繪製遊戲畫面"""
        # 清空螢幕
        self.screen.fill(COLORS["BACKGROUND"])

        # 根據遊戲狀態繪製不同內容
        if self.state in [GameState.PLAYING, GameState.CRAFTING, GameState.SMELTING]:
            self._draw_gameplay()
        elif self.state == GameState.INVENTORY:
            self._draw_inventory()
        elif self.state == GameState.PAUSED:
            self._draw_pause_screen()
        elif self.state == GameState.GAME_OVER:
            self._draw_game_over_screen()

        # 更新顯示
        pygame.display.flip()

    def _draw_gameplay(self) -> None:
        """繪製遊戲進行畫面"""
        if self.cave_system.in_cave:
            # 繪製洞穴場景
            self._draw_cave_scene()
        else:
            # 繪製地表場景（使用相機系統）
            self.world_manager.draw(self.screen, self.camera)

        # 繪製玩家（固定在螢幕中心）
        camera_center_x, camera_center_y = self.camera.get_player_screen_position()
        self.player.draw(self.screen, camera_center_x, camera_center_y)

        # 繪製UI
        self.ui.draw_survival_bars(self.screen, self.player)
        self.ui.draw_time_info(self.screen, self.time_manager)
        self.ui.draw_messages(self.screen, self.messages)

        # 繪製製作/燒製介面
        if self.state == GameState.CRAFTING:
            self.ui.draw_crafting_interface(
                self.screen, self.player, self.world_manager
            )
        elif self.state == GameState.SMELTING:
            self.ui.draw_smelting_interface(self.screen, self.player)

        # 繪製洞穴相關UI
        if self.cave_system.in_cave:
            self._draw_cave_ui()

    def _draw_cave_scene(self) -> None:
        """繪製洞穴場景"""
        # 洞穴背景
        cave_color = (40, 40, 40)  # 深灰色洞穴背景
        self.screen.fill(cave_color)

        # 繪製洞穴牆壁邊界
        wall_color = (20, 20, 20)
        wall_thickness = 20

        # 上牆
        pygame.draw.rect(
            self.screen, wall_color, (0, 0, WINDOW_CONFIG["width"], wall_thickness)
        )
        # 下牆
        pygame.draw.rect(
            self.screen,
            wall_color,
            (
                0,
                WINDOW_CONFIG["height"] - wall_thickness,
                WINDOW_CONFIG["width"],
                wall_thickness,
            ),
        )
        # 左牆
        pygame.draw.rect(
            self.screen, wall_color, (0, 0, wall_thickness, WINDOW_CONFIG["height"])
        )
        # 右牆
        pygame.draw.rect(
            self.screen,
            wall_color,
            (
                WINDOW_CONFIG["width"] - wall_thickness,
                0,
                wall_thickness,
                WINDOW_CONFIG["height"],
            ),
        )

        # 繪製洞穴物件和黑暗效果
        self.cave_system.draw(self.screen, self.camera)

        # 繪製玩家（在洞穴中也固定在螢幕中心）
        camera_center_x, camera_center_y = self.camera.get_player_screen_position()
        self.player.draw(self.screen, camera_center_x, camera_center_y)
        # 繪製出口提示
        exit_text = "按 Enter 鍵退出洞穴"
        font = pygame.font.Font(None, 24)
        text_surface = font.render(exit_text, True, (255, 255, 0))
        self.screen.blit(text_surface, (10, WINDOW_CONFIG["height"] - 40))

    def _draw_cave_ui(self) -> None:
        """繪製洞穴相關UI"""
        # 火把時間指示器
        if self.cave_system.player_torch_time > 0:
            torch_time = int(self.cave_system.player_torch_time)
            torch_text = f"火把剩餘: {torch_time}秒"
            color = (255, 255, 0) if torch_time > 30 else (255, 100, 100)
        else:
            torch_text = "黑暗中！按 L 鍵使用照明"
            color = (255, 0, 0)

        font = pygame.font.Font(None, 20)
        text_surface = font.render(torch_text, True, color)
        self.screen.blit(text_surface, (10, 80))

        # 洞穴深度指示
        if self.cave_system.current_room:
            depth_text = f"洞穴深度: 第 {self.cave_system.current_room.depth} 層"
            depth_surface = font.render(depth_text, True, (200, 200, 200))
            self.screen.blit(depth_surface, (10, 100))

    def _draw_inventory(self) -> None:
        """繪製物品欄畫面"""
        # 先繪製遊戲背景（半透明）
        self._draw_gameplay()

        # 繪製半透明覆蓋層
        overlay = pygame.Surface((WINDOW_CONFIG["width"], WINDOW_CONFIG["height"]))
        overlay.set_alpha(128)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))

        # 繪製物品欄
        self.ui.draw_inventory(self.screen, self.player.inventory)

    def _draw_pause_screen(self) -> None:
        """繪製暫停畫面"""
        # 半透明覆蓋層
        overlay = pygame.Surface((WINDOW_CONFIG["width"], WINDOW_CONFIG["height"]))
        overlay.set_alpha(128)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))

        # 暫停文字
        self.ui.draw_centered_text(
            self.screen,
            "遊戲暫停",
            WINDOW_CONFIG["width"] // 2,
            WINDOW_CONFIG["height"] // 2,
            COLORS["TEXT"],
            "large",
        )

        # 提示文字
        self.ui.draw_centered_text(
            self.screen,
            "按 ESC 繼續遊戲",
            WINDOW_CONFIG["width"] // 2,
            WINDOW_CONFIG["height"] // 2 + 50,
            COLORS["TEXT"],
            "medium",
        )

    def _draw_game_over_screen(self) -> None:
        """繪製遊戲結束畫面"""
        # 半透明覆蓋層
        overlay = pygame.Surface((WINDOW_CONFIG["width"], WINDOW_CONFIG["height"]))
        overlay.set_alpha(200)
        overlay.fill((100, 0, 0))
        self.screen.blit(overlay, (0, 0))

        # 遊戲結束文字
        self.ui.draw_centered_text(
            self.screen,
            "遊戲結束",
            WINDOW_CONFIG["width"] // 2,
            WINDOW_CONFIG["height"] // 2,
            COLORS["DANGER"],
            "large",
        )

        # 統計資訊
        stats_text = f"存活天數: {self.time_manager.current_day}"
        self.ui.draw_centered_text(
            self.screen,
            stats_text,
            WINDOW_CONFIG["width"] // 2,
            WINDOW_CONFIG["height"] // 2 + 50,
            COLORS["TEXT"],
            "medium",
        )

        # 重新開始提示
        self.ui.draw_centered_text(
            self.screen,
            "按 Q 鍵退出遊戲",
            WINDOW_CONFIG["width"] // 2,
            WINDOW_CONFIG["height"] // 2 + 100,
            COLORS["TEXT"],
            "small",
        )

    def run(self) -> None:
        """運行遊戲主迴圈"""
        print("開始遊戲！")

        while self.running:
            # 控制幀率
            self.clock.tick(WINDOW_CONFIG["fps"])

            # 處理事件
            self.handle_events()

            # 更新遊戲邏輯
            self.update()

            # 繪製畫面
            self.draw()

        # 清理資源
        self.music_manager.cleanup()
        self.sound_manager.cleanup()
        pygame.quit()
        print("👋 遊戲結束，感謝遊玩！")


def main():
    """主函數 - 遊戲入口點"""
    try:
        game = Game()
        game.run()
    except Exception as e:
        print(f"遊戲發生錯誤: {e}")
        pygame.quit()
        sys.exit(1)


if __name__ == "__main__":
    main()
