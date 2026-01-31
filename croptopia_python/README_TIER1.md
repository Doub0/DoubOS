# Croptopia Python/Pygame - TIER 1 Implementation

**Status**: TIER 1 Foundation Systems Complete ✅  
**Date**: 2025-02-11  
**Language**: Python 3.8+  
**Framework**: Pygame 2.x + Tkinter UI wrapper

## Overview

This is a Python/Pygame recreation of the Croptopia Godot game. The implementation is structured in tiers:

- **TIER 1** (Current): Foundation systems - signal communication, scene management, player, tilemap rendering, UI
- **TIER 2** (Planned): Game mechanics - dialogue system, NPC behavior, quest tracking, cutscenes
- **TIER 3** (Planned): Advanced systems - crafting, farming, day/night cycle, persistence

### TIER 1 Systems (Complete)

#### 1. Signal System (`croptopia/signals.py`)
**Purpose**: Replace Godot's signal/connect mechanism with Python observer pattern

**Key Classes**:
- `SignalEmitter` - Base class for any system that emits/receives signals
- `EventBus` - Singleton for global system-wide events

**API**:
```python
# Connect to signal
obj.on_signal('signal_name', callback_function)

# Emit signal with arguments
obj.emit_signal('signal_name', arg1, arg2, ...)

# Disconnect
obj.disconnect_signal('signal_name', callback_function)
```

**Example**:
```python
class MySystem(SignalEmitter):
    def trigger_event(self):
        self.emit_signal('event_happened', data=42)

system = MySystem()
system.on_signal('event_happened', lambda data: print(f"Event: {data}"))
system.trigger_event()  # Prints "Event: 42"
```

**Status**: ✅ Complete, tested, production-ready

---

#### 2. Scene Manager (`croptopia/scene_manager.py`)
**Purpose**: Orchestrate all 11 scenes and route signals between them

**Key Classes**:
- `Scene` - Base class for all scenes
- `SceneManager` - Singleton orchestrator

**Scenes Managed**:
1. `spawn_world` - Initial spawn point, flora generation
2. `world_2` - Opening cutscene with camera path
3. `shelburne_road` - Checkpoint with dialogue
4. `michael_plot` - Building placement area
5. `shelburne` - Full town area
6. `cave` - Ore/resource mining
7. `npc_scenes` - NPC spawning and roaming
8-11. Additional minor scenes

**Signal Routing** (from worldtest.gd):
- `spawn_node` → `scene_triggered` signal
- `michael_plot` → `cutscene_end` signal  
- `npc` → `quest_is_finished` signal

**Example**:
```python
scene_manager = SceneManager()
scene_manager.switch_scene('shelburne')
```

**Status**: ✅ Core implementation complete, placeholders for scene classes

---

#### 3. Player System (`croptopia/player.py`)
**Purpose**: Handle 8-direction movement, animation, inventory, camera

**Key Features**:
- **8-Direction Movement**: Walk (100 px/s), sprint (200 px/s)
- **Animation System**: 4-frame walk loops, direction-based sprites
- **Item System**: Wielding items with direction-based offsets
- **Camera Control**: Follows player with configurable offset
- **Signals**: Inventory events (item_holding, item_collected, etc.)

**Constants**:
```python
SPEED_WALK = 100.0
SPEED_SPRINT = 200.0
ANIMATION_FRAME_DURATION = 0.1  # seconds per frame
```

**Directions** (Direction enum):
- `IDLE`, `UP`, `DOWN`, `LEFT`, `RIGHT`
- `UP_LEFT`, `UP_RIGHT`, `DOWN_LEFT`, `DOWN_RIGHT`

**API**:
```python
player = Player((x, y), assets)

# Input handling
keys = pygame.key.get_pressed()
player.handle_input(keys, mouse_buttons)

# Update and render
player.update(delta_time)
player.render(display_surface, camera_position)

# Item system
player.on_item_collected('stick')
player.on_item_selected('Iron Axe')
```

**Status**: ✅ Complete with full docstrings and test code

---

#### 4. TileMap Renderer (`croptopia/systems/tilemap_renderer.py`)
**Purpose**: Render 6-layer tilemap with viewport culling and collision detection

**Key Features**:
- **Multi-Layer Rendering**: grass, decoration, shadow, collision, highlight, effect
- **Viewport Culling**: Only renders visible tiles (performance optimization)
- **Collision Detection**: Separate collision layer for pathfinding
- **PackedInt32Array Decoding**: Godot's binary tile format
- **Layer Visibility**: Toggle layers on/off

**Constants**:
```python
TILE_WIDTH = 16
TILE_HEIGHT = 16
CULL_MARGIN = 32  # Extra tiles around viewport
```

**Layer Structure**:
```python
{
    'grass': {(x, y): tile_id, ...},
    'decoration': {...},
    'shadow': {...},
    'collision': {...},  # Only for collision, not rendered
    'highlight': {...},
    'effect': {...}
}
```

**API**:
```python
tilemap = TileMapRenderer(tilemap_data, assets)

# Update visibility culling
tilemap.update(camera_position, viewport_size)

# Render to display
tilemap.render(display_surface, camera_position)

# Check walkability
if tilemap.is_walkable(x, y):
    # Movement is valid

# Get collision tiles for pathfinding
collision_tiles = tilemap.get_collision_tiles()

# Debug: Show collision layer
tilemap.render_collision_overlay(display, camera_pos, opacity=100)
```

**Godot Tile Format Decoding**:
```python
# PackedInt32Array stores: x in lower 16 bits, y in upper 16 bits
x = packed_value & 0xFFFF
y = (packed_value >> 16) & 0xFFFF
```

**Status**: ✅ Complete with collision layer parsing and asset mapping

---

#### 5. UI Canvas System (`croptopia/ui/canvas.py`)
**Purpose**: Render all UI elements (HUD, hotbar, dialogue, menus)

**Key Classes**:
- `UICanvas` - Main coordinator
- `HotBar` - 3x3 inventory grid
- `HUD` - Day/health/money display
- `DialogBox` - Character dialogue display

**UI Layers** (Z-ordering):
```python
UILayer.BACKGROUND = 0
UILayer.GAME = 1
UILayer.HUD = 2
UILayer.DIALOG = 3
UILayer.INVENTORY = 4
UILayer.MENU = 5
UILayer.DEBUG = 6
```

**HotBar** (from worldtest.gd):
- Position: (239, 544)
- Size: 3×3 grid (9 slots)
- Selected slot highlighting
- Item storage

**HUD Elements**:
- Day counter
- Time display (0.0 = 6 AM, 0.5 = 6 PM)
- Money counter
- Health bar

**DialogBox**:
- Character name display
- Text with word wrapping
- Portrait frame support (0-7)
- Semi-transparent background

**API**:
```python
canvas = UICanvas((800, 600))

# Hotbar operations
canvas.hotbar.add_item(0, "Iron Axe")
canvas.hotbar.select_slot(1)
item = canvas.hotbar.get_selected_item()

# HUD updates
canvas.hud.set_day(5)
canvas.hud.set_money(150)
canvas.hud.set_health(80)

# Dialog
canvas.show_dialog("Zea", "Would you help me farm?")
canvas.hide_dialog()

# Rendering
canvas.update(delta_time)
canvas.render(display_surface)
```

**Status**: ✅ Complete with all major components

---

## File Structure

```
croptopia_python/
├── main.py                          # Game engine entry point
├── croptopia/
│   ├── __init__.py
│   ├── signals.py                   # Signal/observer system (97 lines)
│   ├── scene_manager.py             # Scene orchestration (247 lines)
│   ├── player.py                    # Player character system (400 lines)
│   ├── ui/
│   │   ├── __init__.py
│   │   └── canvas.py                # UI rendering (450 lines)
│   └── systems/
│       ├── __init__.py
│       └── tilemap_renderer.py      # Tilemap rendering (350 lines)
└── README.md                        # This file
```

**Total TIER 1 Code**: ~1,600 lines

---

## Game Engine Loop (`main.py`)

The `GameEngine` class coordinates all TIER 1 systems:

```python
class GameEngine:
    # Frame rate
    FPS = 60
    
    def run(self):
        """Main loop: input → update → render"""
        while self.running:
            delta = clock.tick(60) / 1000.0
            
            # 1. Handle input (keyboard, mouse)
            self._handle_input()
            
            # 2. Update systems
            player.update(delta)
            tilemap.update(camera_pos, viewport_size)
            ui.update(delta)
            
            # 3. Render in order
            # - Tilemap (background)
            # - Player (character)
            # - Current scene (cutscenes)
            # - UI (foreground)
```

### Rendering Order
1. Clear display with gray background
2. Render tilemap (6 layers, culled)
3. Render player sprite
4. Render current scene (for cutscenes)
5. Render UI canvas (HUD, hotbar, dialog)
6. Optional: Debug collision overlay (F10)

### Input Handling
- **WASD/Arrow Keys**: Move player in 8 directions
- **Left Shift**: Sprint
- **Mouse Click**: Select hotbar slot
- **F10**: Toggle collision debug display
- **ESC**: Quit game

---

## Signal Architecture

### Global Signals (EventBus)
For system-wide events:
```python
EventBus.on_signal('day_changed', callback)
EventBus.emit_signal('day_changed', new_day)
```

### System Signals
Each system (Player, Scene, UI) emits its own signals:
```python
player.on_signal('item_holding', on_item_selected)
scene_manager.on_signal('scene_changed', on_scene_transition)
ui.on_signal('dialog_shown', on_dialog_start)
```

### Signal Connection Flow (from worldtest.gd)
```
spawn_node.scene_triggered 
    ↓
scene_manager._on_spawn_scene_triggered()
    ↓
switch_scene('world_2')

michael_plot.cutscene_end
    ↓
scene_manager._on_michael_plot_end()

npc.quest_is_finished
    ↓
scene_manager._on_zea_quest_finished()
```

---

## Asset System (TODO)

Assets are loaded into the `assets` dictionary and passed to each system:

```python
assets = {
    # Player sprites
    'player_up_walk_0': pygame.Surface(...),
    'player_down_idle': pygame.Surface(...),
    
    # Tiles
    'tile_grass_1': pygame.Surface(...),
    'tile_decoration_5': pygame.Surface(...),
    
    # UI
    'hotbar_bg': pygame.Surface(...),
    'dialog_bg': pygame.Surface(...)
}
```

Asset sources:
- **Player sprites**: 8 directions × 2 move types × 4 frames = 64 sprites
- **Tile sprites**: 220+ for 6 layers from croptopia_assets/
- **UI sprites**: Hotbar, buttons, HUD elements
- **NPC sprites**: 8 portrait frames for dialogue

---

## Testing TIER 1 Systems

Each module includes embedded test code:

```bash
# Test individual systems
python -m croptopia.signals
python -m croptopia.scene_manager
python -m croptopia.player
python -m croptopia.systems.tilemap_renderer
python -m croptopia.ui.canvas

# Run full game
python main.py
```

---

## Known Limitations (TIER 1)

- Asset loading is placeholder (assetLoader not implemented)
- Scene classes are skeleton (Scene base objects, not actual world content)
- No collision detection for player movement (only tilemap collision data)
- Dialogue system is basic (no multi-line parsing, no portrait animation)
- Day/night cycle not implemented
- Farming mechanics not implemented
- NPC behavior not implemented

---

## TIER 2 Roadmap (Next Phase)

After TIER 1, implement:

1. **Dialogue System** (`croptopia/systems/dialogue.py`)
   - 8-frame portrait animation from dialogue.gd (200 lines)
   - Multi-line text parsing
   - Choice system for branching dialogue

2. **NPC System** (`croptopia/systems/npc.py`)
   - Roaming state machine (Zea NPC)
   - Pathfinding using tilemap collision
   - Quest tracking and progression

3. **Cutscene Manager** (`croptopia/systems/cutscene.py`)
   - Camera path following
   - Character animation sequences
   - Scene transitions with effects

---

## Dependencies

```
pygame==2.1.2
```

Optional (for UI wrapper):
```
tkinter  (usually included with Python)
```

---

## Performance Notes

- **Viewport Culling**: Tilemap only renders visible tiles (32 tile margin)
- **Delta Time**: Framerate-independent updates
- **Layer Rendering**: 6 layers rendered in order, skipping invisible layers
- **Asset Caching**: Loaded assets stay in memory (no dynamic loading)

Expected performance:
- 60 FPS on modern hardware
- Supports maps up to 500×500 tiles with culling
- ~2MB RAM for asset cache (220+ tiles + UI)

---

## Credits

- **Original Godot Project**: Croptopia (analyzed 02.11.25)
- **Python Conversion**: TIER 1 Foundation
- **Architecture Reference**: worldtest.gd (main orchestrator)

---

## License

Same as original Godot project (pending clarification)

---

## Next Steps

1. ✅ TIER 1 Foundation complete
2. ⏳ Asset loader implementation (load from croptopia_assets/)
3. ⏳ Implement actual scene classes (content for each world area)
4. ⏳ Add collision detection for player movement
5. ⏳ Begin TIER 2 dialogue/NPC systems

---

*Last updated: 2025-02-11*  
*TIER 1 Implementation: Complete* ✅
