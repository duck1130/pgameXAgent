---
mode: agent
---

# 🎮 敲磚塊遊戲開發計畫書

## 📋 專案概述

製作一個經典的敲磚塊遊戲，具備計分系統、多種磚塊類型及特殊能力機制。

**參考來源**: 從 `class3\class3-2.py` 抽取核心功能並擴展

## 🎯 遊戲核心機制

### 基本玩法

- 玩家控制底部擋板左右移動
- 球體在場景中彈跳，碰撞擋板和磚塊
- 目標：消除所有磚塊並獲得高分
- 生命值系統：球體掉出底部扣除生命

### 勝負條件

- **勝利**: 消除所有磚塊
- **失敗**: 生命值歸零

## 🧱 磚塊系統設計

### 磚塊分類與功能

#### 普通磚塊 (80% 比例)

```python
NORMAL_BRICKS = {
    "RED": {
        "color": (255, 100, 100),
        "points": 10,
        "hits_required": 1,
        "special_effect": None
    },
    "ORANGE": {
        "color": (255, 165, 0),
        "points": 15,
        "hits_required": 1,
        "special_effect": None
    },
    "YELLOW": {
        "color": (255, 255, 100),
        "points": 20,
        "hits_required": 1,
        "special_effect": None
    },
    "GREEN": {
        "color": (100, 255, 100),
        "points": 25,
        "hits_required": 1,
        "special_effect": None
    },
    "BLUE": {
        "color": (100, 100, 255),
        "points": 30,
        "hits_required": 1,
        "special_effect": None
    }
}
```

#### 特殊磚塊 (20% 比例)

```python
SPECIAL_BRICKS = {
    "SILVER": {
        "color": (192, 192, 192),
        "points": 50,
        "hits_required": 2,
        "special_effect": "EXTRA_BALL"
    },
    "GOLD": {
        "color": (255, 215, 0),
        "points": 100,
        "hits_required": 1,
        "special_effect": "SCORE_MULTIPLIER"
    },
    "PURPLE": {
        "color": (128, 0, 128),
        "points": 75,
        "hits_required": 1,
        "special_effect": "PADDLE_EXPAND"
    },
    "PINK": {
        "color": (255, 192, 203),
        "points": 60,
        "hits_required": 1,
        "special_effect": "SLOW_BALL"
    },
    "DARK_BLUE": {
        "color": (0, 0, 139),
        "points": 40,
        "hits_required": 3,
        "special_effect": "INDESTRUCTIBLE_TEMP"
    }
}
```

## ⚡ 特殊能力系統

### 能力效果設計

1. **EXTRA_BALL**: 增加一顆球體
2. **SCORE_MULTIPLIER**: 15 秒內得分 x2
3. **PADDLE_EXPAND**: 擋板變大 20 秒
4. **SLOW_BALL**: 球速減半 10 秒
5. **INDESTRUCTIBLE_TEMP**: 磚塊需要多次碰撞才能摧毀

### 能力觸發機制

```python
def trigger_special_effect(brick_type):
    """
    觸發特殊磚塊效果

    Args:
        brick_type (str): 磚塊類型識別
    """
    effects = {
        "EXTRA_BALL": spawn_extra_ball,
        "SCORE_MULTIPLIER": activate_score_boost,
        "PADDLE_EXPAND": expand_paddle,
        "SLOW_BALL": slow_down_ball,
        "INDESTRUCTIBLE_TEMP": None  # 被動效果
    }

    if brick_type in effects and effects[brick_type]:
        effects[brick_type]()
```

## 📊 計分系統

### 得分規則

- **基礎分數**: 根據磚塊顏色
- **連擊加成**: 連續命中磚塊時分數遞增
- **特殊獎勵**:
  - 清除一排磚塊: +500 分
  - 使用特殊能力: +100 分
  - 完美通關(無失球): +1000 分

### 計分板設計

```python
SCORE_SYSTEM = {
    "current_score": 0,
    "high_score": 0,
    "combo_multiplier": 1.0,
    "lives_remaining": 3,
    "level": 1,
    "bricks_destroyed": 0
}
```

## 🎨 視覺設計規劃

### 色彩配置

- **背景**: 深藍色漸層 (0, 0, 50) → (0, 0, 100)
- **擋板**: 銀色 (192, 192, 192)
- **球體**: 白色 (255, 255, 255)
- **UI 元素**: 黃色 (255, 255, 0)

### 佈局設計

```
┌─────────────────────────────────┐
│ 分數: 1250  生命: ♥♥♥  等級: 1  │ ← UI 資訊欄
├─────────────────────────────────┤
│ 🧱🧱🧱🧱🧱🧱🧱🧱🧱🧱🧱🧱 │ ← 磚塊區域
│ 🧱🧱🧱🧱🧱🧱🧱🧱🧱🧱🧱🧱 │   (12x8 排列)
│ 🧱🧱🧱🧱🧱🧱🧱🧱🧱🧱🧱🧱 │
│                               │
│           ⚪                  │ ← 球體
│                               │
│                               │
│            ▬▬▬▬              │ ← 擋板
└─────────────────────────────────┘
```

## 🛠️ 技術實作計畫

### 主要類別架構

```python
# 核心遊戲類別
class BreakoutGame:
    """主遊戲控制器"""
    pass

class Paddle:
    """玩家擋板"""
    pass

class Ball:
    """遊戲球體"""
    pass

class Brick:
    """磚塊基礎類別"""
    pass

class SpecialBrick(Brick):
    """特殊磚塊類別"""
    pass

class ScoreManager:
    """計分系統管理"""
    pass

class EffectManager:
    """特效管理器"""
    pass
```

### 檔案結構規劃

```
pgameXAgent/
├── src/
│   ├── breakout_game.py      # 主遊戲邏輯
│   ├── game_objects.py       # 遊戲物件類別
│   ├── score_system.py       # 計分系統
│   ├── effect_manager.py     # 特效管理
│   └── constants.py          # 遊戲常數定義
├── assets/
│   ├── sounds/               # 音效檔案
│   └── images/               # 圖片資源 (如需要)
└── main.py                   # 遊戲入口點
```

## 🎮 控制機制

### 輸入控制

- **滑鼠位置**: 左右移動擋板但不超出視窗
- **任意鍵**: 發射球體/開始遊戲
- **ESC**: 暫停遊戲

### 物理系統

- 球體彈跳角度計算
- 碰撞偵測優化
- 速度控制機制

## 📈 開發里程碑

### Phase 1: 基礎架構 (預計 2-3 天)

- [ ] 建立專案結構
- [ ] 實作基本遊戲迴圈
- [ ] 創建 Paddle、Ball、Brick 基礎類別
- [ ] 基本碰撞偵測

### Phase 2: 核心功能 (預計 3-4 天)

- [ ] 磚塊排列系統
- [ ] 完整碰撞處理
- [ ] 計分系統實作
- [ ] 生命值機制

### Phase 3: 特殊功能 (預計 2-3 天)

- [ ] 特殊磚塊實作
- [ ] 能力效果系統
- [ ] 視覺特效添加

### Phase 4: 最佳化與潤飾 (預計 1-2 天)

- [ ] 性能優化
- [ ] UI 美化
- [ ] 音效添加 (可選)
- [ ] 測試與除錯

## 🐛 風險評估

### 潛在挑戰

1. **碰撞偵測精度**: 需要精確的球體-磚塊碰撞計算
2. **特效效能**: 多重特效可能影響遊戲流暢度
3. **平衡性調整**: 特殊能力可能過強或過弱

### 解決方案

- 使用成熟的碰撞偵測演算法
- 特效系統採用物件池模式
- 可調整的遊戲參數設定

---
