def draw_crafting_interface(
    self, screen: pygame.Surface, player: "Player", world_manager=None
) -> None:
    """繪製重新設計的製作介面 - 支持滾輪的垂直列表佈局"""
    craft_width = 720
    craft_height = 600
    craft_x = (WINDOW_CONFIG["width"] - craft_width) // 2
    craft_y = (WINDOW_CONFIG["height"] - craft_height) // 2

    # 主背景
    bg_rect = pygame.Rect(craft_x, craft_y, craft_width, craft_height)
    pygame.draw.rect(screen, COLORS["UI_PANEL"], bg_rect)
    pygame.draw.rect(screen, COLORS["UI_BORDER"], bg_rect, 3)

    # 標題區域
    title_rect = pygame.Rect(craft_x, craft_y, craft_width, 60)
    pygame.draw.rect(screen, COLORS["INFO"], title_rect)
    pygame.draw.rect(screen, COLORS["UI_BORDER"], title_rect, 3)

    # 標題文字
    self.draw_centered_text(
        screen,
        "製作工坊",
        craft_x + craft_width // 2,
        craft_y + 30,
        (255, 255, 255),
        "large",
    )

    # 配方資料
    recipe_categories = {
        "基礎工具": {
            "axe": {
                "materials": {"wood": 3, "stone": 2},
                "name": "斧頭",
                "desc": "砍伐樹木的利器",
            },
            "pickaxe": {
                "materials": {"wood": 2, "stone": 3},
                "name": "稿子",
                "desc": "挖掘石頭和礦物",
            },
            "bucket": {
                "materials": {"wood": 4, "stone": 1},
                "name": "木桶",
                "desc": "更有效地飲用河水",
            },
            "torch": {
                "materials": {"wood": 1, "coal": 1},
                "name": "火把",
                "desc": "照亮黑暗的洞穴",
            },
        },
        "建築設施": {
            "workbench": {
                "materials": {"wood": 4},
                "name": "工作台",
                "desc": "製作高級物品必需",
            },
            "furnace": {
                "materials": {"stone": 8},
                "name": "熔爐",
                "desc": "燒製礦物成錠",
            },
        },
        "戰鬥裝備": {
            "iron_sword": {
                "materials": {"iron_ingot": 2, "wood": 1},
                "name": "鐵劍",
                "desc": "強力的戰鬥武器",
            },
            "iron_armor": {
                "materials": {"iron_ingot": 5},
                "name": "鐵甲",
                "desc": "抵禦怪物攻擊",
            },
        },
    }

    # 檢查工作台
    has_workbench = self._player_near_workbench(player, world_manager)

    # 內容區域設定
    content_area = pygame.Rect(
        craft_x + 10, craft_y + 70, craft_width - 20, craft_height - 140
    )

    # 計算總內容高度
    total_items = sum(len(recipes) for recipes in recipe_categories.values()) + len(
        recipe_categories
    )
    total_content_height = total_items * 110  # 每個物品 100px + 間距 10px

    # 限制滾輪範圍
    max_scroll = max(0, total_content_height - content_area.height)
    self.crafting_scroll_offset = max(0, min(self.crafting_scroll_offset, max_scroll))

    # 設置裁剪區域
    screen.set_clip(content_area)

    # 繪製內容
    current_y = content_area.y - self.crafting_scroll_offset
    recipe_index = 1

    for category_name, recipes in recipe_categories.items():
        # 分類標題
        if current_y > content_area.y - 40 and current_y < content_area.bottom + 40:
            category_rect = pygame.Rect(
                content_area.x, current_y, content_area.width, 30
            )
            category_color = (
                COLORS["SUCCESS"]
                if category_name == "基礎工具"
                else (
                    COLORS["INFO"] if category_name == "建築設施" else COLORS["WARNING"]
                )
            )
            pygame.draw.rect(screen, category_color, category_rect)
            pygame.draw.rect(screen, COLORS["UI_BORDER"], category_rect, 2)

            self.draw_centered_text(
                screen,
                category_name,
                content_area.x + content_area.width // 2,
                current_y + 15,
                (255, 255, 255),
                "medium",
            )

        current_y += 40

        # 繪製配方
        for item_id, recipe_data in recipes.items():
            if recipe_index > 8:
                break

            # 只繪製可見區域的物品
            if current_y + 100 > content_area.y and current_y < content_area.bottom:
                # 製作條件檢查
                can_craft_materials = all(
                    player.inventory.has_item(mat, amount)
                    for mat, amount in recipe_data["materials"].items()
                )

                is_basic_craft = item_id in ["workbench"] or category_name == "基礎工具"
                can_craft_location = is_basic_craft or has_workbench
                can_craft = can_craft_materials and can_craft_location

                # 物品背景
                item_rect = pygame.Rect(
                    content_area.x, current_y, content_area.width, 100
                )

                if can_craft:
                    bg_color = (*COLORS["SUCCESS"], 60)
                    border_color = COLORS["SUCCESS"]
                elif can_craft_materials and not can_craft_location:
                    bg_color = (*COLORS["WARNING"], 60)
                    border_color = COLORS["WARNING"]
                else:
                    bg_color = (*COLORS["TEXT_SECONDARY"], 40)
                    border_color = COLORS["TEXT_SECONDARY"]

                pygame.draw.rect(screen, bg_color, item_rect)
                pygame.draw.rect(screen, border_color, item_rect, 2)

                # 數字標籤
                circle_x = content_area.x + 30
                circle_y = current_y + 20
                pygame.draw.circle(screen, (255, 255, 255), (circle_x, circle_y), 15)
                pygame.draw.circle(screen, COLORS["INFO"], (circle_x, circle_y), 15, 2)
                self.draw_centered_text(
                    screen, str(recipe_index), circle_x, circle_y, (0, 0, 0), "medium"
                )

                # 物品名稱
                name_color = (
                    (0, 255, 0)
                    if can_craft
                    else ((255, 255, 0) if can_craft_materials else (200, 200, 200))
                )
                self.draw_text(
                    screen,
                    recipe_data["name"],
                    content_area.x + 60,
                    current_y + 10,
                    name_color,
                    "large",
                )

                # 物品描述
                self.draw_text(
                    screen,
                    recipe_data["desc"],
                    content_area.x + 60,
                    current_y + 35,
                    (220, 220, 220),
                    "medium",
                )

                # 材料需求 - 智能截斷以適應窗口
                materials_parts = []
                for mat, amount in recipe_data["materials"].items():
                    owned = player.inventory.get_item_count(mat)
                    part = f"{mat}×{amount}"
                    if owned < amount:
                        part += f"({owned})"
                    materials_parts.append(part)

                materials_text = "需要: " + ", ".join(materials_parts)

                # 確保文字不超出窗口寬度
                max_width = content_area.width - 70
                if len(materials_text) > 45:  # 粗略計算，如果太長就截斷
                    materials_text = materials_text[:42] + "..."

                self.draw_text(
                    screen,
                    materials_text,
                    content_area.x + 60,
                    current_y + 55,
                    (255, 255, 255),
                    "medium",
                )

                # 製作狀態
                if not is_basic_craft and not has_workbench:
                    self.draw_text(
                        screen,
                        "需要靠近工作台",
                        content_area.x + 60,
                        current_y + 75,
                        (255, 50, 50),
                        "medium",
                    )
                elif can_craft:
                    self.draw_text(
                        screen,
                        f"按 {recipe_index} 鍵製作",
                        content_area.x + 60,
                        current_y + 75,
                        (50, 255, 50),
                        "medium",
                    )
                elif not can_craft_materials:
                    self.draw_text(
                        screen,
                        "材料不足",
                        content_area.x + 60,
                        current_y + 75,
                        (255, 100, 100),
                        "medium",
                    )

            current_y += 110
            recipe_index += 1

    # 移除裁剪
    screen.set_clip(None)

    # 滾輪提示
    if max_scroll > 0:
        scroll_text = f"使用滾輪查看更多 ({self.crafting_scroll_offset}/{max_scroll})"
        self.draw_centered_text(
            screen,
            scroll_text,
            craft_x + craft_width // 2,
            craft_y + craft_height - 50,
            (150, 150, 150),
            "small",
        )

    # 底部資訊
    info_y = craft_y + craft_height - 30
    self.draw_text(
        screen,
        "按數字鍵 1-8 製作 | ESC 退出",
        craft_x + 20,
        info_y,
        (255, 255, 100),
        "medium",
    )

    status_text = "工作台可用" if has_workbench else "需要工作台製作高級物品"
    status_color = (100, 255, 100) if has_workbench else (255, 150, 50)
    self.draw_text(screen, status_text, craft_x + 400, info_y, status_color, "medium")
