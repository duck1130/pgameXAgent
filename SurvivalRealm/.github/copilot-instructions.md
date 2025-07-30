# 🎮 Survival Realm - AI Coding Agent Instructions

## 📋 Project Overview

This is a **2D survival RPG game** built with Pygame, featuring modular architecture. Players collect resources, craft tools, and survive in a dynamically generated world.

## 🏗️ Architecture & Code Organization

### Core Module Structure

```
src/
├── core/config.py          # Central config hub - ALL constants here
├── entities/player.py      # Player class with SurvivalStats dataclass
├── systems/               # Game systems (inventory, time)
├── world/                 # World objects, managers
└── ui/                    # User interface components
```

### Key Architectural Patterns

**Config-Driven Design**: All game parameters live in `src/core/config.py`:

- `WINDOW_CONFIG`, `PLAYER_CONFIG`, `SURVIVAL_STATS`
- `ITEM_RECIPES`, `WORLD_OBJECTS`, `TOOL_EFFICIENCY`
- Colors defined in `COLORS` dict, use descriptive names

**Dataclass for Data Structures**: Use `@dataclass` for game data:

```python
@dataclass
class SurvivalStats:
    health: float = 100.0
    hunger: float = 100.0
    # Updates via delta_time in update() method
```

**Manager Pattern**: Centralized system management:

- `WorldManager` handles object spawning/cleanup
- `TimeManager` controls day/night cycles
- Each manager has `update(delta_time)` and `draw(screen)` methods

## 🎯 Development Conventions

### State Management

```python
# Game states via enum in config.py
class GameState(Enum):
    PLAYING = "playing"
    INVENTORY = "inventory"
    CRAFTING = "crafting"
    # State switches in Game.handle_events()
```

### Game Loop Structure

Standard pattern in `main.py Game.run()`:

1. `handle_events()` - Process input
2. `update(delta_time)` - Game logic
3. `draw()` - Render everything
4. `pygame.display.flip()`

### Type Safety

- Use type hints extensively: `from typing import Optional, List, TYPE_CHECKING`
- Import types conditionally to avoid circular imports

## 🛠️ Key Integration Points

### Adding New Items

1. Define in `inventory.py ItemDatabase.items` dict
2. Add recipe to `config.py ITEM_RECIPES` if craftable
3. Update crafting logic in `main.py _craft_item()`

### Adding World Objects

1. Create class inheriting from `GameObject` in `world/world_objects.py`
2. Implement `draw()` and `interact()` methods
3. Add spawn config to `config.py WORLD_OBJECTS`
4. Register in `WorldManager.create_random_object()`

### UI Extensions

- All UI rendering in `ui/user_interface.py`
- Font handling: Use `UI_CONFIG["font_path"]` with fallbacks
- Message system: `Game.add_message()` with auto-cleanup

## 🔧 Development Workflow

### Running the Game

```bash
cd SurvivalRealm
python main.py
```

### Common Tasks

- **Balance tweaking**: Edit `config.py` values (no restart needed)
- **Debug mode**: Add print statements in update loops
- **New features**: Follow manager pattern, update config first

### File Organization Rules

- **Never hardcode values** - use config.py constants
- **Prefer composition over inheritance** for game objects
- **Keep UI separate** from game logic
- **Use descriptive naming**: `interaction_range` not `range`

## 🎮 Game-Specific Knowledge

### Player Mechanics

- Movement via WASD, speed controlled by `PLAYER_CONFIG["speed"]`
- Survival stats decay over time in `SurvivalStats.update()`
- Tool efficiency multipliers in `TOOL_EFFICIENCY`

### Crafting System

- Recipes defined as material dictionaries in `ITEM_RECIPES`
- Crafting requires proximity to workbench (distance check)
- Smelting uses furnace + fuel consumption logic

### World Generation

- Objects spawn randomly with `spawn_rate` from config
- Safe zone around player prevents spawn overlap
- Continuous spawning via timer in `WorldManager`

## 🐱 Code Style Notes

- Use emoji in comments and prints for personality
- Descriptive variable names: `interaction_cooldown` not `cooldown`
- Keep methods focused: separate `_handle_crafting()` from `_handle_smelting()`
- Document complex calculations with inline comments

## 🚨 Common Gotchas

- **Circular imports**: Use `TYPE_CHECKING` for cross-module references
- **Delta time**: Always use `delta_time` for frame-independent updates
- **Config changes**: Game needs restart for some config changes
- **Font loading**: Handle missing fonts gracefully with fallbacks
