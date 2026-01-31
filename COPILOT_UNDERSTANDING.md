# COPILOT UNDERSTANDING - CROPTOPIA PROJECT

**Updated**: January 30, 2026  
**Status**: FULLY ANALYZED

---

## Critical Understandings

### 1. **NOT A SINGLE MONOLITHIC WORLD**
- ❌ WRONG: Thinking Shelburne is "the main world"
- ✅ CORRECT: Shelburne, world_2, caves, mountains, forests are SEPARATE ZONES
- Each zone is a distinct .tscn file that can be independently loaded
- Zones are connected by transitions/portals defined in scripts
- Player moves BETWEEN zones, not within one massive world

### 2. **SCENE COMPOSITION**
A "scene" in the context of Croptopia means:
- 1x `.tscn` file (scene definition with node hierarchy)
- 1x `.gd` file (GDScript that controls the scene logic)
- Multiple PNG asset files (textures for all nodes in the scene)
- These three work together as a complete system

### 3. **ASSET USAGE**
Every visible element needs:
- Correct PNG file reference
- Correct file path (res://pixilart-file.png format)
- Correct AtlasTexture region (if sprite sheet)
- Correct sprite positioning on canvas

Ground, bushes, buildings, NPCs, crops - ALL require explicit PNG assets.

### 4. **RECIPES & CRAFTING**
- Recipes embedded in .tscn files as node parameters
- Found in crafting_menu.gd and inventory systems
- Items have base prices with inflation modifiers
- Trading/economy managed through NPC signals

### 5. **KEY FILES TO UNDERSTAND**
- `player.tscn` + `unique_player.gd` = Player character
- `world_2.tscn` + `world_2.gd` = Opening/spawn zone  
- `shelburne.tscn` + `shelburne.gd` = Main hub town
- `zea_house.tscn` + `inside_zea_house.gd` = Interior example
- Zone files that reference other .tscn as children

### 6. **NPC SYSTEM**
- NPCs defined in individual .tscn files
- Multiple dialogue scenes per NPC (first_dialogue, second, third, etc.)
- Dialogue triggered by player interaction (E key)
- Quests and rewards assigned through NPC nodes

### 7. **CROP/TREE SYSTEM**
- Each crop type: `.gd` file (logic) + `.tscn` file (node structure) + `.png` files (sprites)
- States: growth stages → ready → harvested → regrow
- Timing: WHEAT_GROWTH_TIME = 3.0 seconds, etc.
- Z-index layering: objects in front if player_y < object_y

---

## What I MUST Do

1. **Read every TSCN file** in order, understanding:
   - Node hierarchy
   - Child scene references ([PackedScene] lines)
   - Attached scripts
   - Texture assignments

2. **Map PNG→Element** for:
   - Every ground tile
   - Every building
   - Every NPC
   - Every crop/tree
   - Every UI element

3. **Extract all recipes** by scanning:
   - crafting_menu.gd
   - inventory.gd
   - All .tscn craft-related nodes

4. **Build zone transition logic** by finding:
   - Area2D trigger areas
   - _on_area_entered() signals
   - Scene.load() or get_tree().change_scene() calls

5. **Recreate in Python** using:
   - Actual PNG files (PIL.Image to load them)
   - Actual scene structure (not placeholder names)
   - Actual zone transitions (not fake movement)
   - Actual recipes (extracted from TSCN)

---

## What NOT To Do

- ❌ Create placeholder sprites
- ❌ Assume world structure
- ❌ Ignore PNG asset paths
- ❌ Simplify scene hierarchies
- ❌ Skip reading any file completely
- ❌ Guess at recipes or mechanics

---

## The Question I Must Ask Before Any Code

**Before writing ANY game code, I must verify:**
1. Which .tscn files should be the starting scenes?
2. What is the correct zone loading sequence?
3. Which PNG files represent ground/terrain?
4. Where are recipes defined exactly?
5. How do zones transition to each other?

I will read the copilot_info folder updates and follow them EXACTLY.

