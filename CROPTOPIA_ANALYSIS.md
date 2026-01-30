# Croptopia Godot Project - Complete Analysis

## PROJECT STRUCTURE
**Location**: C:\Users\F99500\Downloads\Croptopia - 02.11.25
**Engine**: Godot Engine 4.1
**Main Scene**: res://scenes/main.tscn
**Config**: project.godot

## KEY MECHANICS DISCOVERED

### Player System
- **Movement**: 8-directional (up, down, left, right, diagonals)
- **Sprint**: Shift+WASD for faster movement (2x speed)
- **Animation States**: 
  - walk_up, walk_down, walk_left
  - walk_up_idle, walk_down_idle, walk_left_idle
  - Animated sprite with flip_h for left/right reversal
- **Speed**: Base 100 units/sec, Sprint 200 units/sec
- **Inventory System**: 8 hotbar slots
- **Tools**: Axe with swing animations (front, back, left, right)

### Inventory & Item System
- **8 Hotbar Slots**: Numbered 1-8 for quick selection
- **Crop Types Found**:
  - Chives (🌿)
  - Wheat (🌾)
  - Sorrel (🍀)
  - Redbaneberry (❤️)
  - Elderberry (🫐)
  - Cranberry (🍓)
  - Apricorn
  - Pinecone
  - Maple resources
- **Item Holding**: Axe, construction items, crops
- **Resource Files**: .tres format with name, texture, resource_name

### Crop/Item Data
From .tres files found:
```
chives.tres:
  resource_name = "chive"
  name = "Chives"
  
wheat.tres:
  name = "Wheat"
  
sorrel.tres:
  resource_name = "sorrel"
  name = "Sorrel"
  
redbaneberry.tres:
  name = "Redbaneberry"
  
elderberry.tres:
  name = "Elderberry"
  
cranberry.tres:
  name = "Cranberry"
```

### Control Scheme (Input Actions)
- **Movement**: W/A/S/D (up/left/down/right)
- **Sprint**: Shift + WASD
- **Inventory**: I key
- **Interact**: E key
- **Tool Use**: Left Click
- **Tool Toggle**: C key (chat/tool switch)
- **Hotbar**: 1-8 keys for slot selection
- **Menu**: Escape key
- **Save**: K key
- **Load**: L key

### Save System
- **Save Path**: user://Saves/
- **Save File**: PlayerSave.tres
- **Save Data**: Position (Save_pos), inventory state
- **Load**: Restores position and inventory

### World Features Found
- **Buildings**: Houses (type 1, 2, 3), caves, NPCs
- **Trees**: Birch, Oak, Maple, Elderberry, Mediumspruce
- **Collectibles**: Pinecones, sticks, various berries
- **Tools**: Axe (with slash animations), flint
- **Decorations**: Grass, bushes, fences, logs
- **NPCs**: Multiple NPC types with dialogue and quest systems

### Audio System
- **Background Music**: mainmenuahh song.mp3, Main_menu_.wav
- **Sound Effects**: Various WAV/MP3 files
- **Audio Settings**: audio_settings.gd for volume control

### Scene System
- **Main Menu**: game_menu.tscn
- **World Map**: Multiple scenes with transitions
- **UI Scenes**: hotbar.tscn, inventory UI, crafting menus
- **Dialogue System**: Dialogue player with character interactions

### Advanced Features
1. **Day/Night Cycle**: day_and_night.gd (timed progression)
2. **Crafting System**: crafting_menu.gd
3. **Shop System**: leo_alcohol_shop.gd (buying/selling)
4. **Building Placement**: build_placable.gd
5. **NPC Interactions**: npc.gd, npc_quest.gd (dialogue trees)
6. **Enemy System**: Enemy test scenes
7. **Economy Manager**: economy_manager.gd (currency tracking)
8. **Game Data**: GameData.gd (global state management)
9. **Load Manager**: LoadManager.gd (save/load functionality)
10. **Shader Effects**: color_depth.gdshader, highlow.gdshader

## SIGNALS & EVENTS
Player signals:
- stick_collected, stick_held
- baneberry_held, pinecone_collected
- elderberry_collected, sorrel_collected
- redbane_collected, chive_collected
- slot_1_selected through slot_8_selected
- tool_hit (when swinging tool)
- item_holding (when holding an item)
- world_disable_building

## THEMES & AESTHETICS
- **Pixel Art**: Pixilart style graphics
- **Color Palette**: Dark backgrounds, bright UI accents
- **UI Font**: Adobe Pixel font
- **Resolution**: Viewport stretch mode
- **Boot Splash**: Custom pixil-frame image

## KEY LEARNINGS FOR IMPLEMENTATION
1. **8-Directional Movement** with animations
2. **Hotbar System** with 8 selectable slots
3. **Multiple Crop Types** (minimum 7 crops)
4. **Tool/Item System** with visual representations
5. **Inventory Tracking** with quantities
6. **Day/Night Progression** mechanics
7. **Save/Load System** for persistence
8. **Shop/Economy** for buying/selling
9. **Crafting/Building** placeable items
10. **NPC Interaction** with dialogue
11. **Audio** for ambiance and effects
12. **Keyboard Controls** (1-8 hotbar, WASD movement, E interact, C tool)
13. **Smooth Animations** and visual feedback
14. **Resource Management** (energy/stamina system)
