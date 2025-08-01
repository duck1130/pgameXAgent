# 🎮 Survival Realm - AI 硬漢貓咪開發指南 🐱

## 📋 Project Overview

**Survival Realm** 是一款使用 Pygame 開發的 **2D 生存 RPG 遊戲**，採用完全重構的模組化架構 (v3.2.0)。玩家需要收集資源、製作工具、在晝夜循環中對抗怪物並建造建築物。最新版本新增了**相機系統**、洞穴探險系統、主動攻擊怪物 AI 和稀有河流機制。程式碼遵循嚴格的配置驅動設計，具有集中式狀態管理和完整的型別註解。

### 🚨 重要架構提醒

**統一現代化架構** (已驗證 ✅):
- `src/` 目錄：完整的模組化架構 (v3.2.0) - **當前使用**
- `main.py`：主程式入口點，完整功能實現，系統初始化正常
- 不再有舊架構或 `main_old.py`，專案已完成現代化重構
- 全螢幕模式預設啟用：`WINDOW_CONFIG["fullscreen"]: True` (實測：1440x900)

**虛擬環境狀態**:
- 專案包含 `.venv/` 虛擬環境，已安裝 Pygame 2.6.1
- 開發前先啟用：`source .venv/bin/activate` (macOS/Linux) 或 `.venv\Scripts\activate` (Windows)
- Python 版本：3.13.5
- 狀態：已測試，系統初始化正常 ✅


## 🏗️ 核心架構與設計模式

### 模組化結構 (重構後)

```
src/
├── core/config.py          # 🎯 所有遊戲常數、枚舉、跨平台配置  
├── entities/player.py      # 🏃 Player 類與 SurvivalStats dataclass
├── systems/               # 🔧 遊戲系統 (inventory, camera, time_manager, music_manager)
│   ├── camera.py          # 📷 相機跟隨系統 (v3.1.0 新增)
│   └── ...
├── world/                 # 🌍 世界物件、world_manager、GameObject 基類
│   ├── cave_system.py     # 🕳️ 洞穴探險系統 (v3.1.0 新增)
│   └── world_objects.py   # 各種世界物件類別
└── ui/                    # 📱 UI 系統與字體回退處理
assets/
├── sounds/                # 🎵 音樂和音效檔案
│   ├── minecraft_background.wav  # 背景音樂
│   ├── minecraft_night.wav       # 夜間音樂
│   └── minecraft/               # Minecraft 風格音效庫
└── sprites/               # 🎨 圖像和精靈檔案
    ├── player_skins/      # 玩家皮膚和物品圖示
    └── terrain/           # 地形材質檔案
```

### 關鍵架構模式

**配置驅動一切**: 所有常數集中在 `src/core/config.py`：

- `WINDOW_CONFIG`, `PLAYER_CONFIG`, `SURVIVAL_STATS` 字典
- `ITEM_RECIPES`, `WORLD_OBJECTS`, `TOOL_EFFICIENCY`, `CAVE_CONFIG` 定義所有遊戲機制
- `COLORS` 字典使用語義化鍵名：`"HEALTH"`, `"DANGER"`, `"UI_PANEL"`, `"TEXT_SECONDARY"`  
- 跨平台字體回退：`get_font_config()` 處理 macOS/Windows/Linux 字體
- 遊戲狀態枚舉：`GameState.PLAYING/CRAFTING/SMELTING/INVENTORY`

**管理器模式**: 每個系統都有專用管理器與標準介面：

- `WorldManager` - 生成、清理、碰撞、回合制怪物更新
- `TimeManager` - 晝夜循環、怪物生成觸發器
- `MusicManager` - 情境感知音樂 (晝夜主題)
- `Camera` - 玩家中心視角、世界座標轉換 (v3.1.0)
- `CaveSystem` - 洞穴探險、深度管理、洞穴怪物系統 (v3.1.0)
- 所有管理器：`update(delta_time)` + `draw(screen)` 方法

**Dataclass + 型別安全**: 大量使用 `@dataclass` 和型別提示：

```python
@dataclass 
class SurvivalStats:
    health: float = 100.0
    hunger: float = 100.0
    # 總是在 update() 方法中透過 delta_time 更新
```

**TYPE_CHECKING 模式**: 避免循環引入：
```python
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..world.world_manager import WorldManager
```

## 🎯 狀態管理與遊戲循環

### 複雜狀態系統

遊戲使用基於枚舉的狀態與雙模式標誌在 `main.py Game` 類中：

```python
class GameState(Enum):
    PLAYING = "playing"      # 正常遊戲
    INVENTORY = "inventory"   # I 鍵切換  
    CRAFTING = "crafting"    # C 鍵 + 距離檢查
    SMELTING = "smelting"    # S 鍵 + 熔爐距離
    PAUSED = "paused"        # ESC 鍵切換
```

**關鍵狀態邏輯**: 雙重驗證系統防止 bug：
- 狀態枚舉：`self.state == GameState.CRAFTING` 
- 模式標誌：`player.crafting_mode == True`
- 在 `_handle_number_key()` 中同時檢查製作/燒製動作

### 遊戲循環結構  

`main.py Game.run()` 中的標準 delta-time 模式：

1. `self.clock.tick(WINDOW_CONFIG["fps"])` - 幀率控制
2. `handle_events()` - 輸入處理、狀態轉換與除錯記錄
3. `update(delta_time)` - 所有系統以幀時間更新
4. `draw()` - 基於狀態的渲染管線
5. `pygame.display.flip()` - 緩衝區交換

**關鍵更新順序**: Player → Camera → WorldManager (含回合制怪物邏輯) → TimeManager → 訊息清理

## 🎥 相機系統架構 (v3.1.0)

### 核心概念

**玩家固定螢幕中心**: 玩家永遠位於螢幕中央，世界物件隨相機移動：

```python
# 相機座標轉換的關鍵模式
def world_to_screen(self, world_x: float, world_y: float) -> Tuple[int, int]:
    screen_x = world_x - self.world_x + self.screen_center_x
    screen_y = world_y - self.world_y + self.screen_center_y
    return int(screen_x), int(screen_y)
```

**物件繪製適配**: 所有繪製都必須透過相機轉換：
- `GameObject.draw(screen, camera_x, camera_y)` - 基類抽象方法
- `WorldManager.draw(screen, camera)` - 只繪製可見物件
- 玩家固定繪製在 `(screen_center_x, screen_center_y)`

**世界邊界管理**: 玩家移動限制改為世界邊界而非螢幕邊界：
```python
# 在 Player.update() 中的世界邊界檢查
if new_x < -WORLD_BOUNDARY or new_x > WORLD_BOUNDARY:
    return  # 阻止越界移動
```

## 🛠️ 開發工作流程

### 環境設定與依賴

**Python 環境要求**:
- Python 3.8+ (專案使用 Python 3.13.5)
- Pygame 2.6.1+
- 專案包含 `.venv/` 虛擬環境

**環境啟用**:
```bash
# macOS/Linux
source .venv/bin/activate

# Windows
.venv\Scripts\activate
```

### 執行與測試

```bash
cd SurvivalRealm

# 啟用虛擬環境 (如果存在)
source .venv/bin/activate  # macOS/Linux
# 或 .venv\Scripts\activate  # Windows

# 主遊戲執行
python main.py                    # 主遊戲入口點

# 快速功能測試腳本 - 驗證系統導入
python -c "from main import Game; game = Game(); print('✅ 遊戲初始化成功')"
```

### 測試與驗證

目前專案採用輕量級測試方式，已驗證運行正常 ✅：

```bash
# 主遊戲執行
python main.py                    # 主遊戲入口點

# 快速功能測試腳本 - 驗證系統導入
python -c "from main import Game; game = Game(); print('✅ 遊戲初始化成功')"

# 音響系統測試
python -c "
import pygame.mixer
pygame.mixer.init()
print('🎵 音響系統正常')
pygame.mixer.quit()
"

# 模組導入測試
python -c "
from src.core.config import WINDOW_CONFIG, COLORS, GameState
from src.systems.inventory import item_database
from src.world.cave_system import cave_system
from src.systems.camera import camera
print('✅ 所有核心模組導入成功')
"
```

**除錯功能**: 遊戲打印大量狀態轉換記錄，便於開發調試：
- `🔄 狀態變化: PLAYING -> CRAFTING` (狀態變化)
- `🎯 調試：收到數字鍵 4，當前狀態: CRAFTING` (輸入除錯)
- 製作嘗試前的材料/物品欄狀態
- `🕳️ 洞穴系統：進入深度 2，生成 3 個怪物` (洞穴除錯)
- `📷 相機系統：玩家移動到 (150.5, -200.3)` (相機跟隨除錯)
- `🧱 測試洞穴邊界系統...` (洞穴邊界測試記錄)
- 系統初始化會顯示詳細的載入過程和字體發現狀況

**重要提醒**: 專案已完成現代化重構，統一使用 `src/` 目錄下的新架構進行開發。

### 關鍵整合點

**添加物品** (4步驟流程):
1. 在 `src/systems/inventory.py ItemDatabase._initialize_items()` 中定義，附帶 ItemType 枚舉
2. 將製作配方添加到 `src/core/config.py ITEM_RECIPES` 字典
3. 更新 `main.py _craft_item()` 方法中的製作邏輯  
4. 如需要則添加到 UI 製作清單

**添加世界物件**:
1. 在 `src/world/world_objects.py` 中創建繼承 `GameObject` 的類
2. 實作抽象的 `draw()` 和 `interact()` 方法  
3. 將生成配置添加到 `src/core/config.py WORLD_OBJECTS`，包含 spawn_rate/color/size
4. 在 `src/world/world_manager.py _spawn_object()` 中註冊並引入類別

**UI 變更**: 所有渲染都集中在 `src/ui/user_interface.py`：
- 使用強健的 `get_font_config()` 跨平台字體回退
- 來自 `COLORS` 字典的語義化顏色鍵
- 具錯誤處理的多字體載入

**相機系統整合** (重要！):
- 所有 `GameObject` 子類必須實作 `draw(screen, camera_x, camera_y)` 方法
- 世界物件座標轉換：`screen_x = world_x - camera_x + screen_center_x`
- 在 `main.py` 中：`self.camera = camera` (全域單例)
- 相機更新：`self.camera.update(player_center_x, player_center_y, delta_time)`

### 關鍵慣例

- **絕不硬編碼數值** - 專門使用 config.py 常數，甚至顏色/尺寸
- **到處使用 delta time** - 所有更新必須使用 `delta_time` 來保持幀率獨立
- **強制型別安全** - 使用 `TYPE_CHECKING` 引入避免循環依賴  
- **距離驗證** - 工具/製作需要距離計算：`player.x + player.width // 2`  
- **狀態管理** - 切換遊戲狀態時總是重設 `player.crafting_mode`/`smelting_mode`
- **除錯記錄** - 狀態變化使用描述性的打印語句配表情符號前綴

## 🎮 遊戲專用機制

### 玩家系統

- 移動：WASD 鍵，速度來自 `PLAYER_CONFIG["speed"]` (200 像素/秒)
- 生存狀態：在 `SurvivalStats.update(delta_time)` 中使用配置速率自動衰減
- 裝備系統：工具在 `TOOL_EFFICIENCY` 中有效率倍數 
- 互動：透過 `PLAYER_CONFIG` 可配置範圍/冷卻時間，防止垃圾點擊
- **回合制標誌**: `player.has_moved_this_turn` 觸發怪物移動

### 製作與燒製系統

**製作模式**:
- 基礎製作：工作台可在任何地方製作 (`item_id == "workbench"`)
- 高級製作：需要工作台接近度 (`_is_near_workbench()` 檢查 80 像素範圍)

**燒製**: 需要熔爐接近度 + 燃料消耗：
- 材料：`{"iron_ore": 1}` + 燃料 (`coal` 或 `wood`)  
- 驗證：進入燒製模式前的距離檢查
- 資源順序：優先煤炭勝過木材作為燃料

**配方系統**: 配方為 `ITEM_RECIPES` 中的材料字典：
```python
"iron_sword": {"iron_ingot": 2, "wood": 1}  # 材料 + 數量
```

### 世界生成與管理

**動態生成**: `WorldManager` 持續生成系統：
- 玩家周圍安全區域 (`WORLD_CONFIG["safe_zone_radius"]`: 60 像素)
- 基於時間的生成：怪物只在夜間透過 `TimeManager.is_night_time()` 生成
- 回合制怪物移動：由 `player_moved` 標誌觸發
- 清理系統：達到最大數量 (`WORLD_CONFIG["max_objects"]`) 時移除物件

**物件類別**:
- **靜態**: Tree、Rock、River、Cave (可採集/互動)
- **動態**: Monster (朝玩家移動，黎明時死亡)  
- **互動**: Chest、Food (拾取物品)
- **玩家建造**: Workbench、Furnace (透過 P 鍵放置)
- **洞穴物件**: CaveMonster、CaveTreasure、CaveMineral (洞穴專用)

### 進階遊戲系統

**基於時間邏輯**: `TimeManager` 驅動多個系統：
- 晝夜循環：600 秒實際時間 = 1 遊戲日
- 怪物生成：只在 `is_night_time()` 期間 
- 音樂切換：透過 `MusicManager.update_music_for_state()` 晝夜主題
- 怪物死亡：透過 `update_slow_movement(..., is_day_time)` 黎明時自動

**回合制怪物系統**: 怪物只在玩家移動時移動：
- 玩家在移動期間設定 `has_moved_this_turn` 標誌
- `WorldManager.update()` 將標誌傳遞給怪物 `update_slow_movement()`
- 防止怪物壓倒靜止的玩家

### 洞穴探險系統 (v3.1.0)

**洞穴結構**: 每個洞穴有多層深度，使用 `CaveRoom` dataclass 管理：
- 深度系統：1-7 層，越深越危險
- 黑暗機制：`darkness_level` 影響視野和傷害
- 動態生成：每層有不同的怪物、寶藏和礦物分佈

**洞穴怪物 AI**: `CaveMonster` 繼承 `GameObject`，具有主動攻擊行為：
- 狀態機：`patrolling` → `chasing` → `attacking`
- 攻擊範圍：`attack_range`, `chase_range` 可配置
- 智能追擊：主動朝玩家移動，比地表怪物更強大

**照明系統**: 玩家需要火把或洞穴燈才能安全探險：
- 黑暗傷害：沒有照明會持續受到傷害
- 照明工具：火把 (消耗品) 或洞穴燈 (永久)
- 按 `L` 鍵使用照明工具

**洞穴整合**: 在 `main.py` 中：
```python
from src.world.cave_system import cave_system
self.cave_system = cave_system
self.pending_cave_entry = None  # 管理洞穴進入狀態
```

## 常見問題與解決方案

### 🔧 架構過渡期特殊注意事項

**主程式檔案狀態**:
- `main.py` 為當前主程式入口點，包含完整遊戲功能
- 開發時使用 `python main.py` 執行遊戲
- 所有相對導入路徑指向 `src/` 新架構
- Game 類在 `main.py` 中，管理所有系統初始化

**模組導入模式**:
```python
# 標準導入模式（在 main.py 中）
from src.core.config import WINDOW_CONFIG, COLORS, GameState
from src.systems.inventory import item_database
from src.world.cave_system import cave_system
from src.systems.camera import camera  # 單例相機系統
```

**全螢幕配置**:
- 遊戲預設啟用全螢幕模式 (`WINDOW_CONFIG["fullscreen"]: True`)
- 視窗尺寸動態偵測：`WINDOW_CONFIG["width/height"]` 由系統設定
- 相機系統使用動態螢幕中心：`screen_center_x/y = width//2, height//2`

### 測試架構 (輕量級)
- **無傳統測試檔案**: 採用快速 Python 腳本驗證系統功能
- **系統測試**: `python -c "from main import Game; game = Game()"` 驗證初始化
- **模組測試**: 直接導入測試特定系統功能 
- **相機測試**: `from src.systems.camera import camera` 測試相機系統
- **洞穴測試**: `from src.world.cave_system import cave_system` 測試洞穴功能
- **已驗證狀態**: 所有核心模組導入正常，系統初始化成功 ✅

**快速測試模式**:
```bash
# 標準系統初始化測試
python -c "from main import Game; game = Game(); print('✅ 遊戲系統正常')"
```

### 架構陷阱
- **循環引入**: 總是使用 `TYPE_CHECKING` 模式處理跨模組型別提示
- **狀態失同步**: 在輸入處理器中雙重檢查狀態枚舉和模式標誌  
- **距離計算錯誤**: 使用玩家中心點 (`x + width//2`)，不是左上角
- **配置重載**: 字體路徑、視窗大小變更需要完全重啟遊戲

### 效能與記憶體
- **距離優化**: 對接近度檢查使用距離平方 (`**2`)，避免 sqrt
- **物件清理**: `WorldManager` 自動移除非活動物件以防止記憶體洩漏  
- **訊息系統**: 自動清理計時器防止無限訊息累積
- **字體回退**: 多字體載入優雅處理缺失的系統字體

### 遊戲邏輯 Bug  
- **材料驗證**: 在製作中總是原子性地檢查和消耗材料
- **模式重設**: 變更狀態時清除製作/燒製模式 (ESC 鍵)
- **接近度快取**: 距離檢查代價昂貴，盡可能快取結果
- **除錯記錄**: 狀態轉換除錯對複雜輸入處理必不可少

## 🐱 程式碼風格與專案文化

### 程式碼庫個性
- **表情符號註解**: 在打印語句中使用描述性表情符號：`🎯 調試：`, `✅ 成功：`, `❌ 錯誤：`
- **雙語命名**: 英文程式碼/中文註解混合反映開發團隊文化
- **詳細除錯**: 開發期間的廣泛狀態日誌有助於除錯
- **硬漢貓咪團隊**: 在整個程式碼庫中引用「硬漢貓咪開發團隊 🐱」

### 技術標準
- **描述性變數**: `interaction_cooldown` 而非 `cooldown`，`crafting_mode` 而非 `mode`
- **方法粒度**: 分割複雜處理器 (`_handle_crafting()` vs `_handle_smelting()`)  
- **訊息回饋**: 對所有玩家通知使用 `Game.add_message()` 並自動清理
- **跨平台感知**: 字體/路徑處理考慮 Windows/macOS/Linux 差異
- **文檔字串完整性**: 所有方法都有 Args/Returns/Raises 文檔

---

## 🚀 快速開發參考

### ⚡ 最重要的檔案 (開發優先級)

1. **`main.py`** - 主程式入口點，完整功能實現
2. **`src/core/config.py`** - 所有遊戲參數和配置
3. **`src/systems/inventory.py`** - 物品系統管理
4. **`src/world/world_manager.py`** - 世界物件生成和管理
5. **`src/world/cave_system.py`** - 洞穴探險系統
6. **`src/systems/camera.py`** - 相機跟隨系統

### ⚡ 常用開發命令

```bash
# 執行遊戲
python main.py

# 快速測試系統是否正常
python -c "from main import Game; game = Game()"

# 測試洞穴系統
python -c "from src.world.cave_system import cave_system; print('洞穴系統正常')"

# 測試相機系統
python -c "from src.systems.camera import camera; print('相機系統正常')"
```

### ⚡ 架構陷阱速查

- ❌ 不要忘記 `TYPE_CHECKING` 處理循環引用
- ❌ 不要硬編碼數值，使用 `config.py` 常數
- ❌ 不要使用玩家左上角座標，使用中心點計算距離
- ✅ 所有系統都要有 `update(delta_time)` 和 `draw()` 方法
- ✅ 相機系統中所有物件繪製需要座標轉換
- ✅ 狀態變更時記得雙重檢查枚舉和模式標誌

---

*外表硬漢，內心溫柔，代碼專業！這就是硬漢貓咪開發團隊的座右銘！(ˊ・ω・ˋ)* 🐱
