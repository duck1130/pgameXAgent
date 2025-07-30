# 🎮 Survival Realm - AI Coding Agent Instructions

## 📋 Project Overview

**Survival Realm** is a **2D survival RPG game** built with Pygame, featuring a modular architecture. Players collect resources, craft tools, and survive in a dynamically generated world. The codebase follows a config-driven design with centralized state management.

## 🏗️ Architecture & Core Patterns

### Module Structure

```
src/
├── core/config.py          # ALL game constants and configuration
├── entities/player.py      # Player class with SurvivalStats dataclass
├── systems/               # Game systems (inventory, time_manager)
├── world/                 # World objects and world_manager
└── ui/                    # User interface components
```

### Critical Architectural Patterns

**Config-Driven Everything**: All constants live in `src/core/config.py`:

- Window, player, survival stats config dictionaries
- `ITEM_RECIPES`, `WORLD_OBJECTS`, `TOOL_EFFICIENCY` define game mechanics
- `COLORS` dict with descriptive keys like `"HEALTH"`, `"DANGER"`, `"UI_PANEL"`
- Cross-platform font fallback system in `get_font_config()`

**Manager Pattern**: Each system has a dedicated manager:

- `WorldManager` - object spawning, cleanup, collision detection
- `TimeManager` - day/night cycles, time progression
- All managers implement `update(delta_time)` and `draw(screen)` methods

**Dataclass for Game Data**: Use `@dataclass` for structured data:

```python
@dataclass
class SurvivalStats:
    health: float = 100.0
    hunger: float = 100.0
    # Always updated via delta_time in update() method
```

## 🎯 State Management & Game Loop

### State System

Game states defined as enum in `config.py`:

```python
class GameState(Enum):
    PLAYING = "playing"
    INVENTORY = "inventory"
    CRAFTING = "crafting"
    SMELTING = "smelting"
```

State transitions handled in `Game.handle_events()` via keyboard input.

### Game Loop Structure

Standard pattern in `main.py Game.run()`:

1. `handle_events()` - Process input, state switches
2. `update(delta_time)` - Update all systems with frame time
3. `draw()` - Render based on current state
4. `pygame.display.flip()`

## 🛠️ Development Workflow

### Running & Testing

```bash
cd SurvivalRealm
python main.py
```

**Debug Output**: Game prints initialization status and controls on startup. Check terminal for errors.

### Key Integration Points

**Adding Items**:

1. Define in `inventory.py ItemDatabase.items` dict with ItemType enum
2. Add crafting recipe to `config.py ITEM_RECIPES`  
3. Update crafting logic in `main.py _craft_item()` and UI crafting interfaces

**Adding World Objects**:

1. Create class inheriting `GameObject` in `world/world_objects.py`
2. Implement required `draw()` and `interact()` methods
3. Add spawn configuration to `config.py WORLD_OBJECTS`
4. Register in `WorldManager.create_random_object()` and import in `world_manager.py`

**UI Changes**: All rendering in `ui/user_interface.py`, uses robust font fallback system

### Critical Conventions

- **Never hardcode values** - use config.py constants exclusively
- **Delta time everywhere** - all updates must use `delta_time` for frame independence  
- **Type safety**: Use `TYPE_CHECKING` imports to avoid circular dependencies
- **Proximity checks**: Tools/crafting require distance calculations to workbench/furnace
- **Center-point calculations**: Use `player.x + player.width // 2` for distance checks
- **State management**: Reset `player.crafting_mode`/`smelting_mode` when changing game states

## 🎮 Game-Specific Mechanics

### Player System

- Movement: WASD keys, speed from `PLAYER_CONFIG["speed"]`
- Survival stats decay automatically in `SurvivalStats.update(delta_time)` 
- Equipment system: tools have efficiency multipliers in `TOOL_EFFICIENCY`
- Interaction range: configurable via `PLAYER_CONFIG["interaction_range"]`
- **Interaction cooldown**: `PLAYER_CONFIG["interaction_cooldown"]` prevents spam

### Crafting & Smelting

- **Crafting**: Workbench proximity required (except basic workbench crafting)
- **Smelting**: Furnace proximity + fuel consumption (coal/wood)  
- Recipes as material dictionaries: `{"wood": 3, "stone": 2}`
- Resource validation before material consumption
- **Building placement**: Player can place workbench/furnace via P key

### World Generation

- Continuous spawning system with timer in `WorldManager`
- Safe zone around player prevents spawn conflicts
- Each object type has spawn rate probability in config
- Dynamic object cleanup when max count reached
- **Object types**: Tree, Rock, Food, River, Chest, Cave, Monster, plus player-placed buildings

### State Management Deep Dive

Game uses enum-based states in `main.py Game` class:
- **State transitions**: ESC toggles between PLAYING/PAUSED, number keys trigger crafting
- **Mode flags**: `player.crafting_mode` and `player.smelting_mode` control UI and input
- **Proximity validation**: Crafting/smelting check workbench/furnace distance before allowing mode entry

##  Common Issues & Solutions

- **Circular imports**: Always use `TYPE_CHECKING` for cross-module type hints
- **State desync**: Ensure crafting/smelting modes reset when changing states
- **Distance calculations**: Use player center point, not top-left corner
- **Config reload**: Some changes require game restart (font paths, window size)
- **Performance**: Use distance squared for proximity checks, avoid expensive calculations in tight loops
- **Font issues**: Multi-platform font fallback system handles missing fonts gracefully
- **Memory management**: World objects auto-cleanup prevents infinite spawning

## 🐱 Code Style & Project Culture

- **Personality**: Use emoji in comments and console output (・ω・)
- **Naming**: Descriptive variables (`interaction_cooldown` not `cooldown`)  
- **Method separation**: Split complex handlers (`_handle_crafting()` vs `_handle_smelting()`)
- **Message system**: `Game.add_message()` for player feedback with auto-cleanup timer
- **Documentation**: Extensive docstrings with Args/Returns/Raises sections
- **Error handling**: Graceful fallbacks, especially for cross-platform compatibility

````
