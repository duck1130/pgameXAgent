# 🎮 Survival Realm - AI Coding Agent Instructions

## 📋 Project Overview

**Survival Realm** is a **2D survival RPG game** built with Pygame, featuring a fully refactored modular architecture (v3.1.0). Players collect resources, craft tools, survive day/night cycles with monsters, and build structures in a dynamically generated world. The codebase follows strict config-driven design with centralized state management and comprehensive type annotations.

## 🏗️ Architecture & Core Patterns

### Modular Structure (Post-Refactor)

```
src/
├── core/config.py          # ALL game constants, enums, cross-platform configs  
├── entities/player.py      # Player class with SurvivalStats dataclass
├── systems/               # Game systems (inventory, time_manager, music_manager)
├── world/                 # World objects, world_manager, GameObject base class
└── ui/                    # UI system with fallback font handling
```

### Critical Architectural Patterns

**Config-Driven Everything**: All constants centralized in `src/core/config.py`:

- `WINDOW_CONFIG`, `PLAYER_CONFIG`, `SURVIVAL_STATS` dictionaries 
- `ITEM_RECIPES`, `WORLD_OBJECTS`, `TOOL_EFFICIENCY` define all game mechanics
- `COLORS` dict with semantic keys: `"HEALTH"`, `"DANGER"`, `"UI_PANEL"`, `"TEXT_SECONDARY"`
- Cross-platform font fallback: `get_font_config()` handles macOS/Windows/Linux fonts
- Game state enums: `GameState.PLAYING/CRAFTING/SMELTING/INVENTORY`

**Manager Pattern**: Each system has dedicated manager with standard interface:

- `WorldManager` - spawning, cleanup, collision, turn-based monster updates
- `TimeManager` - day/night cycles, monster spawning triggers
- `MusicManager` - context-aware music (day/night themes)
- All managers: `update(delta_time)` + `draw(screen)` methods

**Dataclass + Type Safety**: Extensive use of `@dataclass` and type hints:

```python
@dataclass 
class SurvivalStats:
    health: float = 100.0
    hunger: float = 100.0
    # Always updated via delta_time in update() method
```

**TYPE_CHECKING Pattern**: Avoid circular imports:
```python
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..world.world_manager import WorldManager
```

## 🎯 State Management & Game Loop

### Complex State System

Game uses enum-based states with dual-mode flags in `main.py Game` class:

```python
class GameState(Enum):
    PLAYING = "playing"      # Normal gameplay
    INVENTORY = "inventory"   # I key toggle  
    CRAFTING = "crafting"    # C key + proximity checks
    SMELTING = "smelting"    # S key + furnace proximity
    PAUSED = "paused"        # ESC key toggle
```

**Critical State Logic**: Dual validation system prevents bugs:
- State enum: `self.state == GameState.CRAFTING` 
- Mode flags: `player.crafting_mode == True`
- Both checked in `_handle_number_key()` for crafting/smelting actions

### Game Loop Structure  

Standard delta-time pattern in `main.py Game.run()`:

1. `self.clock.tick(WINDOW_CONFIG["fps"])` - Frame rate control
2. `handle_events()` - Input processing, state transitions with debug logging
3. `update(delta_time)` - All systems updated with frame time
4. `draw()` - State-based rendering pipeline
5. `pygame.display.flip()` - Buffer swap

**Key Update Order**: Player → WorldManager (with turn-based monster logic) → TimeManager → Message cleanup

## 🛠️ Development Workflow

### Running & Testing

```bash
cd SurvivalRealm
python main.py                    # Main game
python tests/test_game_systems.py # Comprehensive integration tests
python tests/run_tests.py         # Test runner
```

**Debug Features**: Game prints extensive state transition logs:
- `🔄 狀態變化: PLAYING -> CRAFTING` (state changes)
- `🎯 調試：收到數字鍵 4，當前狀態: CRAFTING` (input debugging)
- Material/inventory status before crafting attempts

### Key Integration Points

**Adding Items** (4-step process):
1. Define in `inventory.py ItemDatabase._initialize_items()` with ItemType enum
2. Add crafting recipe to `config.py ITEM_RECIPES` dict
3. Update crafting logic in `main.py _craft_item()` method  
4. Add to UI crafting lists if needed

**Adding World Objects**:
1. Create class inheriting `GameObject` in `world/world_objects.py`
2. Implement abstract `draw()` and `interact()` methods  
3. Add spawn config to `config.py WORLD_OBJECTS` with spawn_rate/color/size
4. Register in `WorldManager._spawn_object()` and import in world_manager.py

**UI Changes**: All rendering centralized in `ui/user_interface.py`:
- Uses robust `get_font_config()` cross-platform font fallback
- Semantic color keys from `COLORS` dict
- Multi-font loading with error handling

### Critical Conventions

- **Never hardcode values** - use config.py constants exclusively, even for colors/sizes
- **Delta time everywhere** - all updates must use `delta_time` for frame-rate independence
- **Type safety mandatory** - use `TYPE_CHECKING` imports to avoid circular dependencies  
- **Proximity validation** - tools/crafting require distance calculations: `player.x + player.width // 2`  
- **State management** - always reset `player.crafting_mode`/`smelting_mode` when changing game states
- **Debug logging** - use descriptive print statements with emoji prefixes for state changes

## 🎮 Game-Specific Mechanics

### Player System

- Movement: WASD keys, speed from `PLAYER_CONFIG["speed"]` (200 px/sec)
- Survival stats: Auto-decay in `SurvivalStats.update(delta_time)` using config rates
- Equipment system: tools have efficiency multipliers in `TOOL_EFFICIENCY` 
- Interaction: configurable range/cooldown via `PLAYER_CONFIG` prevents spam-clicking
- **Turn-based flag**: `player.has_moved_this_turn` triggers monster movement

### Crafting & Smelting Systems

**Crafting Modes**:
- Basic crafting: Workbench can be crafted anywhere (`item_id == "workbench"`)
- Advanced crafting: Requires workbench proximity (`_is_near_workbench()` checks 80px range)

**Smelting**: Furnace proximity required + fuel consumption:
- Materials: `{"iron_ore": 1}` + fuel (`coal` or `wood`)  
- Validation: Distance check before entering smelting mode
- Resource order: Prefer coal over wood as fuel

**Recipe System**: Recipes as material dictionaries in `ITEM_RECIPES`:
```python
"iron_sword": {"iron_ingot": 2, "wood": 1}  # Materials + quantities
```

### World Generation & Management

**Dynamic Spawning**: `WorldManager` continuous generation system:
- Safe zone around player (`WORLD_CONFIG["safe_zone_radius"]`: 60px)
- Time-based spawning: monsters only at night via `TimeManager.is_night_time()`
- Turn-based monster movement: triggered by `player_moved` flag
- Cleanup system: removes objects when max count (`WORLD_CONFIG["max_objects"]`) reached

**Object Categories**:
- **Static**: Tree, Rock, River, Cave (can be harvested/interacted with)
- **Dynamic**: Monster (moves toward player, dies at dawn)  
- **Interactive**: Chest, Food (pickup items)
- **Player-Built**: Workbench, Furnace (placed via P key)

### Advanced Game Systems

**Time-Based Logic**: `TimeManager` drives multiple systems:
- Day/night cycle: 600 second real-time = 1 game day
- Monster spawning: only during `is_night_time()` 
- Music switching: day/night themes via `MusicManager.update_music_for_state()`
- Monster death: automatic at dawn via `update_slow_movement(..., is_day_time)`

**Turn-Based Monster System**: Monsters move only when player moves:
- Player sets `has_moved_this_turn` flag during movement
- `WorldManager.update()` passes flag to monster `update_slow_movement()`
- Prevents monsters from overwhelming stationary players

##  Common Issues & Solutions

### Architecture Pitfalls
- **Circular imports**: Always use `TYPE_CHECKING` pattern for cross-module type hints
- **State desync**: Dual-check both state enum AND mode flags in input handlers  
- **Distance calc errors**: Use player center point (`x + width//2`), not top-left corner
- **Config reload**: Font paths, window size changes require full game restart

### Performance & Memory
- **Distance optimization**: Use distance squared (`**2`) for proximity checks, avoid sqrt
- **Object cleanup**: `WorldManager` auto-removes inactive objects to prevent memory leaks  
- **Message system**: Auto-cleanup timer prevents infinite message accumulation
- **Font fallback**: Multi-font loading handles missing system fonts gracefully

### Game Logic Bugs  
- **Material validation**: Always check AND consume materials atomically in crafting
- **Mode reset**: Clear crafting/smelting modes when changing states (ESC key)
- **Proximity caching**: Distance checks are expensive, cache results when possible
- **Debug logging**: State transition debugging essential for complex input handling

## 🐱 Code Style & Project Culture

### Codebase Personality
- **Emoji comments**: Use descriptive emoji in print statements: `🎯 調試：`, `✅ 成功：`, `❌ 錯誤：`
- **Bilingual naming**: Mix of English code/Chinese comments reflects development team culture
- **Verbose debugging**: Extensive state logging during development aids debugging
- **Hardman Cat Team**: References to "硬漢貓咪開發團隊 🐱" throughout codebase

### Technical Standards
- **Descriptive variables**: `interaction_cooldown` not `cooldown`, `crafting_mode` not `mode`
- **Method granularity**: Split complex handlers (`_handle_crafting()` vs `_handle_smelting()`)  
- **Message feedback**: Use `Game.add_message()` for all player notifications with auto-cleanup
- **Cross-platform aware**: Font/path handling considers Windows/macOS/Linux differences
- **Docstring completeness**: All methods have Args/Returns/Raises documentation

````
