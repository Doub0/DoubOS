# Croptopia Knowledge Base

## Project Overview

**Croptopia** is a complete 2D farming/RPG game being ported from Godot to Python. It's integrated into the DoubOS operating system simulator as a playable game within the OS.

### Key Info
- **Original Engine**: Godot (Godot-style node architecture in Python)
- **Current Implementation**: Python with Tkinter GUI and PIL for graphics
- **Story Setting**: Shelburne farming community with a mysterious cult plot and urbanization threat
- **Main Character**: Michael View
- **Asset Path**: Godot project assets stored in `croptopia_assets/` folder

---

## Core Game Systems

### 1. Node-Based Architecture
- Mimics Godot's scene tree system
- **Base Node Class**: Foundation for all game objects
- **Node2D**: 2D nodes with position, rotation, and scale
- **Vector2**: 2D vector math system
- **Signal System**: Godot-style signal/callback communication between nodes

### 2. Item System
```
ItemType Enum:
- CROP: Plantable crops
- COLLECTABLE: Items found in the world
- TREE: Trees with fruit
- TOOL: Equipment/tools
- BUILDING: Structures player can place

Item Properties:
- name, item_type, image_name
- stackable (boolean)
- quantity (stack count)
```

### 3. Crop System
**CropData Structure**:
- `crop_type`: Type of crop
- `growth_stage`: 0=seed, 1=sprout, 2=grown, 3=harvestable
- `x, y`: Grid position
- `plant_time`: Timestamp for growth calculation

### 4. Tree System
**TreeData Structure**:
- `tree_type`: Type of tree
- `x, y`: Grid position
- `has_fruit`: Whether tree currently has fruit
- `regrow_time`: Regrowth timer

### 5. NPC System
**NPCData Structure**:
- `name`: NPC name
- `x, y`: Position in world
- `dialogue_lines`: List of dialogue strings
- `image_name`: Asset reference

---

## Asset Management

### AssetManager Class
- Discovers all PNG assets in the croptopia_assets folder
- Caches loaded images to optimize performance
- Supports resizing with LANCZOS resampling
- Provides fallback/placeholder system for missing assets

### Key Assets
- Character sprites (boycat_walkcycle.png, boykisser.gd)
- Crops (apricorn.tres, chive_collectable.gd, cranberry_bush.gd, etc.)
- Tools (axe.gd, axeslashing.png)
- Trees (birch_tree.tscn, birch_collectable.gd)
- Bushes (bush_des_2.tscn, bush_v_2.tscn)
- Buildings and structures
- UI elements (canvas_layer.tscn, ColorRect.gd)
- Dialogue/Story elements

---

## Game Features

### Gameplay Mechanics
- **Farming**: Plant seeds, watch crops grow through stages, harvest
- **Foraging**: Collectibles (chives, apricorns, etc.)
- **Fishing**: Fish in water areas
- **Mining**: Extract resources from caves
- **Crafting**: Combine items to create new items
- **Building**: Place structures on the farm
- **NPCs & Dialogue**: Interact with story characters

### Story Elements
- Mysterious cult threat
- Urbanization threatening the farming community
- Character interactions and relationships
- Multiple dialogue lines per NPC

---

## File Structure

### Main Implementation Files
- `croptopia_complete.py`: Full implementation with all systems
- `croptopia_ultimate_complete.py`: Latest/ultimate version
- `croptopia_engine.py`: Core Godot-style engine (node system, signals, vector math)
- `croptopia_enhanced*.py`: Various enhanced/optimized versions
- `croptopia_sim.py`: Simulation version
- `croptopia_authentic.py`: Authentic recreation from original assets

### Asset Directories
- `croptopia_assets/`: Contains all Godot scene files (.tscn), scripts (.gd), resources (.tres), and images (.png.import files)

### Documentation
- Multiple markdown guides (CROPTOPIA_UPGRADE.md, CROPTOPIA_V3_ENHANCED.md, etc.)
- ULTIMATE_CROPTOPIA_GUIDE.md: Comprehensive guide
- GAMEPLAY_SHOWCASE.md: Features showcase

---

## Technical Implementation Details

### Data Structures
- Uses Python `@dataclass` decorator for clean data representation
- Enums for type safety (ItemType, growth stages, etc.)
- Dictionary-based caching for assets and game data

### Graphics System
- **Tkinter Canvas**: Main rendering backend
- **PIL (Pillow)**: Image loading and manipulation
- **ImageTk.PhotoImage**: Tkinter-compatible image format
- Sprite scaling and composition

### Input/Interaction
- Keyboard controls (likely WASD or arrow keys)
- Mouse interaction for UI and object selection
- Tool/Item hotkeys

---

## Integration with DoubOS

**Croptopia** is a game application that runs within the DoubOS operating system:
- Accessible through the games menu (`games_menu.py`)
- Integrated as a windowed application
- Can be launched from the OS shell or GUI

---

## Key Concepts

### Godot Pattern in Python
The engine implements Godot design patterns:
- **Scene Tree**: Hierarchical node structure
- **Signals**: Event system for node communication
- **_ready()**: Called when node enters scene
- **_process(delta)**: Frame update loop
- **_physics_process(delta)**: Physics frame update

### Growth Cycle
Crops follow a 4-stage growth cycle:
1. Seed (stage 0)
2. Sprout (stage 1)
3. Grown (stage 2)
4. Harvestable (stage 3)

### Grid-Based World
- 2D grid positioning system
- X, Y coordinates for all entities
- Tile-based farm layout

---

## Python Implementation (croptopia_final.py)

The complete Python recreation uses:
- **Node System**: Godot-style scene tree with proper inheritance
  - `Node`: Base class with signals and child management
  - `Node2D`: 2D transforms (position, rotation, scale, z_index)
  - `CharacterBody2D`: Physics bodies for characters
  - `Area2D`: Detection areas for pickups and interactions
  - `AnimatedSprite2D`: Animation with frame management

- **Game Classes**:
  - `Player`: Michael View with inventory (8 slots), movement, and item collection
  - `CropBase`: Base crop with growth states (no_crop → ready)
  - `TreeBase`: Trees with regrowth timer
  - `NPC`: Characters with dialogue system
  - `World`: Main scene containing all entities
  - `CroptopiaFinal`: Game engine with rendering and input

- **Key Systems**:
  - **Signal System**: Godot-style callbacks for inter-node communication
  - **Asset Manager**: PNG loading and caching from croptopia_assets
  - **Input Handling**: Arrow keys for movement, E for interact
  - **Rendering**: Tkinter Canvas with camera follow
  - **Physics**: Simplified movement with position updates
  - **Game Loop**: 60 FPS with delta time management

## Running the Game

```bash
python croptopia_final.py
```

Controls:
- Arrow Keys: Move player
- E: Interact (harvest crops, talk to NPCs)
- 1-8: Select inventory slots

## Development Status

**COMPLETE**: 1:1 Python recreation of Godot Croptopia
- ✓ Node system fully implemented
- ✓ Player with inventory and movement
- ✓ Crop and tree systems with growth/regrowth
- ✓ NPC dialogue framework
- ✓ Asset loading from croptopia_assets
- ✓ Game loop and rendering
- ✓ Input handling
- ✓ Camera following player

The project demonstrates a complete and faithful port of a Godot game to Python, maintaining the original architecture while being optimized for pure Python execution.
