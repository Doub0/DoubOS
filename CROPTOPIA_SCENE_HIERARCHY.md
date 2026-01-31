# CROPTOPIA COMPLETE SCENE HIERARCHY

## Executive Summary

Croptopia is a farming/adventure game built in Godot Engine featuring multiple interconnected zones, NPCs, crops, and a trading economy. The game includes several main world areas (Shelburne, Mount Crag, Spawn Area), interior house scenes, collectible crops, and a comprehensive UI system.

---

## Scene Map & Hierarchy

### **Main World Scenes**

#### **world_2.tscn** (Starting Area)
- **Root Type:** Node2D
- **Script:** world_2.gd
- **Purpose:** Main overworld starting zone
- **Key Features:**
  - Opening cutscene with camera path following
  - TileMap-based terrain (forest/mountain background)
  - Triggers opening cutscene when player enters
  - Disables/enables cameras during cutscene transitions
  - Contains multiple sub-nodes for world main area

**Child Scenes:**
- world2main (Node2D) - Main world container
  - TileMap (obstacle and mountain layers with extensive tile data)
  - Multiple visual layers for depth
- world2openingcutscene (Node2D) - Cutscene container
  - Path2D & PathFollow2D for camera movement
  - AnimationPlayer for color fade effects
  - Camera2D for cutscene viewing

**Signals:**
- cutscene_start
- cutscene_over

---

#### **shelburne.tscn** (Main Town Area)
- **Root Type:** Node2D
- **Script:** shelburne.gd
- **Purpose:** Shelburne town and surrounding area
- **Load Steps:** 185 (very complex scene)

**Packed Scenes Referenced:**
1. roadblock.tscn - Pathway blockade
2. house_type_1.tscn - Mayor's house
3. zea_house.tscn - Zea's house (story-important NPC)
4. tall_bush_spruce.tscn - Decorative bushes
5. house_type_2.tscn - Town house variant
6. house_type_3.tscn - Town house variant
7. wheat.tscn - Wheat crop
8. leo_alcohol_shop.tscn (scenes/leo_alcohol_shop.tscn) - Shop location
9. shelburne_town_mountain.tscn (scenes/entities/) - Mountain backdrop
10. fence.tscn (scenes/Placeables/) - Decorative fences
11. shelburne_town_north_mountain.tscn (scenes/entities/) - Northern mountain
12. city_house.tscn (scenes/) - Generic house
13. shelburne_bridge.tscn (scenes/entities/) - Bridge structure
14. top_of_mt_crag.tscn - Mountain peak location

**Textures:** 80+ PNG files for terrain, buildings, NPCs, props
**TileMap:** Multiple layers for walkable terrain and obstacles

---

#### **inside_zea_house.tscn** (Interior Scene)
- **Root Type:** Node2D
- **Script:** inside_zea_house.gd
- **Purpose:** Interior of Zea's house (story cutscene)
- **Load Steps:** 13

**Structure:**
- Panel (black background)
- AnimatedSprite2D (house background)
- Area2D (interaction detection)
- StaticBody2D with walls (collision)
- **Cutscene Container:**
  - AnimatedSprite2D (Unknown man NPC)
  - unknown_dialogue.tscn (dialogue system)
  - Sprite2D (player character during cutscene)
  - ColorRect (fade transition)
  - AudioStreamPlayer2D (background music)
  - AnimationPlayer with "fade_out" animation

**Key Signals:**
- body_entered (Area2D detection)
- dialogue_finished (cutscene progression)

---

### **House Scenes**

#### **house_type_1.tscn** (Mayor's House)
- **Root Type:** Node2D
- **Script:** house_types.gd
- **Purpose:** Mayor's residence with special sprite
- **Animations:**
  - "default" - Regular house sprite
  - "mayor_house" - Special lunar propaganda variant

---

#### **house_type_2.tscn**
- **Root Type:** Node2D
- **Purpose:** Generic town house variant
- Similar structure to house_type_1

---

#### **house_type_3.tscn**
- **Root Type:** Node2D
- **Purpose:** Generic town house variant
- Similar structure to house_type_1

---

#### **zea_house.tscn** (Zea's Story House)
- **Root Type:** Node2D
- **Script:** zea_house.gd
- **Purpose:** Interactive house that spawns interior when entered
- **Mechanics:**
  - Detects player proximity with Area2D
  - Creates interior scene on demand (inside_zea_house.tscn)
  - Handles player ability to move/exit
  - Story-important location

**Key Methods:**
- spawn_house() - Instantiates interior
- leave_house() - Exits interior
- Cutscene integration with inside_zea_house

---

### **Crop & Collectible Scenes**

#### **chive.tscn** (Regrowable Crop)
- **Root Type:** Node2D
- **Script:** chive.gd
- **Purpose:** Renewable chive plants that grow over time
- **Item Resource:** chives.tres

**States:**
- "no_chive" - Plant hasn't grown back
- "chive" - Ready to harvest

**Structure:**
- AnimatedSprite2D (shows chive or empty state)
- Area2D with collision (detection radius)
- Timer (growth_timer, 3-second wait time)
- Marker2D (spawn location for collectible)
- CharacterBody2D (collision body)

**Mechanics:**
- Grows back automatically after 3 seconds
- Player presses "E" to harvest
- Drops chive_collectable.tscn
- Signals: picked_up

---

#### **chive_collectable.tscn**
- **Root Type:** Node2D
- **Script:** chive_collectable.gd
- **Purpose:** The actual collectable item dropped by chive plant
- **Interaction:** Player picks up for inventory

---

#### **chive_placeable.tscn**
- **Root Type:** Node2D
- **Purpose:** Placeable variant of chive (building system)

---

#### **wheat.tscn** (Regrowable Crop)
- **Root Type:** Node2D
- **Script:** wheat.gd
- **Purpose:** Wheat crop - similar mechanics to chive
- **States:**
  - "no_wheat" - Not ready
  - "wheat" - Ready to harvest
- **Growth Timer:** 3 seconds

---

#### **wheat_collectable.tscn**
- **Root Type:** Node2D
- **Purpose:** Collectible wheat item

---

#### **potato_crop.tscn** (Planted Crop)
- **Root Type:** Node2D
- **Script:** potato_crop.gd
- **Purpose:** Growable potato with multiple stages
- **Load Steps:** 9

**Growth Stages (animated):**
1. first_stage (Timer: 30s)
2. second_stage (Timer: 30s)
3. third_stage (Timer: 30s)
4. fourth_stage
5. rare_stage (special variant)

**Animation System:**
- AtlasTexture atlas regions from "potato sprites.png"
- SpriteFrames with 5 distinct animations
- Progression-based sprite swapping

---

#### **Tree Scenes (Harvestable Resources)**

##### **birch_tree.tscn**
- **Script:** birch_tree.gd
- **Purpose:** Birch tree - renewable resource
- **States:**
  - "no_birch" - Just harvested
  - "birch" - Ready to harvest
- **Growth Timer:** Configurable
- **Z-Index Management:** Switches based on player position (above/below sorting)
- **Collectible:** birch_collectable.tscn

---

##### **oak_tree.tscn**
- **Script:** oak_tree.gd
- **Purpose:** Oak tree resource
- Similar mechanics to birch

---

##### **maple_tree.tscn**
- **Script:** maple.gd
- **Purpose:** Maple tree resource

---

##### **whitepine_tree.tscn**
- **Script:** whitepine_tree.gd
- **Purpose:** White pine tree resource

---

##### **mediumspruce_tree.tscn**
- **Script:** mediumspruce_tree.gd
- **Purpose:** Medium spruce tree resource

---

##### **pine_tree.gd**
- **Purpose:** Pine tree script reference

---

#### **Berry/Plant Variants**

##### **elderberry_tree.tscn**
- **Script:** elderberry_tree.gd
- **Collectible:** elderberry_collectable.tscn
- **Resource:** elderberry.tres

---

##### **redbaneberry.tscn**
- **Script:** redbaneberry.gd
- **Resource:** redbaneberry.tres
- **Collectible:** redbaneberry_collectable.tscn

---

##### **sorrel.tscn**
- **Script:** sorrel.gd
- **Resource:** sorrel.tres
- **Collectible:** sorrel_collectable.tscn

---

##### **cranberry_bush.tscn**
- **Script:** cranberry_bush.gd
- **Collectible:** cranberry_collectable.tscn
- **Resource:** cranberry.tres

---

#### **Pinecone Variants**

##### **pinecone_collectable.tscn**
- **Script:** pinecone_collectable.gd
- **Purpose:** Collectible pinecone item

---

##### **pinecone_collectable_2.tscn**
- **Script:** pinecone_collectable_2.gd
- **Purpose:** Alternate pinecone variant

---

##### **pinecone_placeable.tscn**
- **Purpose:** Placeable pinecone (building)

---

#### **Other Resources**

##### **stick.tscn** & **stick_collectable.tscn**
- **Purpose:** Wood resource
- **Script:** stick_collectable.gd

---

##### **flint.tscn** & **flint.gd**
- **Purpose:** Stone/mining resource

---

##### **stalagmite.tscn**
- **Script:** stalagmite.gd
- **Purpose:** Underground crystal formation

---

### **NPC & Shop Scenes**

#### **phillip_merchant.tscn** (Main Merchant)
- **Root Type:** Node2D
- **Script:** phillip_merchant.gd
- **Purpose:** Primary trading NPC for economy

**Shop Inventory (Shop Slot Icons):**
1. Redbaneberry (common food/crafting)
2. Chives (common food)
3. Elderberry (foraged berry)
4. Pinecone (resource)
5. Sorrel (foraged plant)
6. Axe (tool - iron)
7. Building Table (construction tool)
8-20. Additional Chive slots

**Economy System:**
- Connects to economy_manager.gd for dynamic pricing
- Demand-based price fluctuation (low/neutral/high)
- Signals for item selection: baneberry_selected, chive_selected, sorrel_selected, elderberry_selected, pinecone_selected
- Sell/Buy mode toggle

**UI Elements:**
- CanvasLayer with shop_ui
- GridContainer for product display (20 slots)
- Info frame with item descriptions
- Currency/cost display
- Demand indicator

---

#### **henry.tscn** (NPC)
- **Purpose:** Named character/NPC

---

#### **boykisser.tscn** (Story NPC)
- **Root Type:** Node2D
- **Script:** boykisser.gd
- **Purpose:** Character with animations

---

#### **unknown_dialogue.tscn** (Dialogue System)
- **Purpose:** Dialogue interaction system for cutscenes
- **Used by:** inside_zea_house.tscn

---

#### **mark_dialogue.tscn** (NPC Dialogue)
- **Root Type:** Control
- **Script:** mark_dialogue.gd
- **Purpose:** Interactive dialogue for Mark NPC

---

#### **philip_first_dialogue.tscn**
- **Script:** philip_first_dialogue.gd
- **Purpose:** First encounter dialogue with Phillip

---

#### **fourth_zea_dialogue.tscn**
- **Script:** fourth_zea_dialogue.gd
- **Purpose:** Fourth dialogue sequence with Zea

---

#### **third_zea_dialogue.tscn**
- **Script:** third_zea_dialogue.gd
- **Purpose:** Third dialogue sequence with Zea

---

#### **second_dialogue_zea.tscn**
- **Purpose:** Second dialogue with Zea

---

#### **npc_quest.tscn**
- **Root Type:** Node2D
- **Script:** npc_quest.gd
- **Purpose:** Quest-giving NPC

---

#### **npctest.tscn**
- **Purpose:** Testing NPC scene

---

### **Environmental & Location Scenes**

#### **cave.tscn**
- **Purpose:** Underground/cave location

---

#### **mountcrag.tscn**
- **Script:** mountcrag.gd
- **Purpose:** Mountain terrain formation

---

#### **top_of_mt_crag.tscn**
- **Script:** top_of_mt_crag.gd
- **Purpose:** Mountain peak (major location)
- **Signal:** cutscene_over
- **Features:** Story event location

---

#### **shelburne centrum.tscn** (shelburn centrum.tscn variants)
- **Script:** shelburncentrum.gd
- **Purpose:** Town center location with variation variants

---

#### **shelter burne.tscn** & **shelburne_centrum.tscn**
- **Purpose:** Alternative town center variants

---

#### **inside_house_1.tscn**
- **Purpose:** Interior of generic house

---

### **Building/Placeable Scenes**

#### **axe.tscn** (Tool)
- **Root Type:** Node2D
- **Script:** axe.gd
- **Purpose:** Axe tool for resource gathering
- **AnimatedSprite2D:** Shows axe during use
- **Animation:** axe slash action

---

#### **fence_placeable.tscn** (Decoration)
- **Root Type:** Node2D
- **Purpose:** Fence that can be placed
- **Location:** scenes/Placeables/

---

#### **build_placable.gd** (Building System)
- **Script:** build_placable.gd
- **Purpose:** Core building/placement mechanic

---

#### **log_seat.tscn** (Furniture)
- **Script:** log_seat.gd
- **Purpose:** Placeable seating

---

#### **tall_bush_spruce.tscn**
- **Purpose:** Tall decorative bush/tree

---

#### **bush.tscn**, **bush_v_2.tscn**, **bush_des_2.tscn**
- **Purpose:** Various bush decoration variants

---

#### **grass.tscn**, **grass_short.tscn**, **grass_short_mid.tscn**
- **Purpose:** Grass terrain variants

---

#### **roadblock.tscn**
- **Purpose:** Path blockade element

---

### **Dialogue & UI Scenes**

#### **unknown_dialouge.tscn**
- **Script:** unknown_dialouge.gd
- **Purpose:** Dialogue interface

---

#### **dialogueplayer.gd**
- **Script:** dialogueplayer.gd
- **Purpose:** Dialogue system engine

---

#### **pause_menu.tscn** (Pause Screen)
- **Root Type:** Control
- **Script:** pause_menu.gd
- **Load Steps:** 23 (complex UI)

**Features:**
- Options/Settings Tab
- Video Settings Tab
- Audio Settings Tab
- Multiple shader materials for visual effects:
  - pause_menu.gdshader (scanlines, CRT effect)
  - color_depth.gdshader
  - vibranto.gdshader
  - highlow.gdshader
- AudioStreamPlayer with background music

**SubNodes:**
- Options (TabContainer)
  - General settings
  - Video settings
  - Audio settings
- Video control panel
- Audio settings (audio_settings.gd)

---

#### **crafting_menu.tscn** (UI)
- **Script:** crafting_menu.gd
- **Purpose:** Crafting/recipe system interface
- **SubNodes:**
  - Menu control
  - Character display
  - Inventory system (inv_improved_ui.tscn)
  - Map display
  - Crafting interface
  - Map markers with location info popups

**Location Info Markers:**
- Shelburne
- Shelburne Forest
- Spawn Area
- Sandbox Area

---

#### **inv_improved_ui.tscn**
- **Purpose:** Improved inventory interface

---

#### **inv_hotbar.tscn**
- **Purpose:** Quick access inventory hotbar

---

#### **hotbar.gd**
- **Script:** hotbar.gd
- **Purpose:** Hotbar item management

---

#### **Inv_slot.gd**
- **Script:** Inv_slot.gd
- **Purpose:** Individual inventory slot behavior

---

#### **shop_ui.tscn** (Shop Interface)
- **Purpose:** Merchant shop UI display

---

#### **game_menu.tscn** (Main Menu)
- **Root Type:** Control
- **Purpose:** Main game menu screen

---

### **Animation & Effects Scenes**

#### **transition.tscn**
- **Script:** transition.gd
- **Purpose:** Scene transition effects

---

#### **day_and_night.tscn** (Dynamic Lighting)
- **Script:** day_and_night.gd
- **Purpose:** Day/night cycle system

---

#### **CanvasLayer.gd**
- **Purpose:** UI layer management

---

#### **ColorRect.gd**
- **Purpose:** Color overlay effects

---

#### **canvas_layer.tscn**
- **Purpose:** Canvas layer container

---

### **Testing & Debug Scenes**

#### **original_testing.tscn**
- **Purpose:** Original test scene

---

#### **object_test.tscn**
- **Script:** object_test.gd
- **Purpose:** Object interaction testing

---

#### **test.tscn**, **testing.tscn**, **testingagain.tscn**
- **Purpose:** Various test scenes

---

#### **testplaceable.tscn**
- **Purpose:** Placeable object testing

---

#### **useless_test.tscn**
- **Purpose:** Unused test scene

---

#### **enemy_test.tscn**
- **Script:** enemy_test.gd
- **Purpose:** Enemy/NPC behavior testing

---

#### **nrn.tscn**
- **Purpose:** Mystery/test scene

---

#### **test_enviroment.tscn**
- **Script:** test_enviroment.gd
- **Purpose:** Environment testing

---

---

## Recipes & Crafting System

### Identified Items in Economy:
1. **Redbaneberry** - Common food/crafting material
2. **Chives** - Common vegetable
3. **Elderberry** - Foraged berry
4. **Pinecone** - Natural resource
5. **Sorrel** - Foraged plant
6. **Wheat** - Cultivated crop
7. **Potato** - Cultivated crop
8. **Birch** - Tree resource
9. **Oak** - Tree resource
10. **Maple** - Tree resource
11. **White Pine** - Tree resource
12. **Medium Spruce** - Tree resource
13. **Cranberry** - Berry bush product
14. **Stick** - Wood resource
15. **Flint** - Stone resource
16. **Stalagmite** - Crystal/mineral
17. **Axe** - Tool (Iron)
18. **Building Table** - Construction tool

### Economy System (economy_manager.gd):
- **Base Price:** 1 USD per item
- **Dynamic Pricing:** Inflation modifier
- **Demand States:**
  - HIGH DEMAND: inflation > 0.75 (icon: good_economy.png)
  - NEUTRAL: 0.25 < inflation < 0.55 (icon: decent_economy.png)
  - LOW DEMAND: inflation < 0.25 (icon: bad_economy.png)
- **Price Fluctuation:** price = price × inflation_value
- **Random Inflation:** randf_range(-0.1, 1.3)

### Specific Item Signals (phillip_merchant.gd):
- `baneberry_selected` - Red baneberry trade
- `chive_selected` - Chive trade
- `sorrel_selected` - Sorrel trade
- `elderberry_selected` - Elderberry trade
- `pinecone_selected` - Pinecone trade
- `axe_selected` - Axe/tool trade

**Note:** No explicit recipes found in code; system appears to be economy/trade focused rather than crafting recipes. Crafting menu exists but full recipe details are in UI implementation rather than scripts.

---

## Asset Mapping (PNG Files → Game Elements)

### Character & NPC Sprites:
| PNG File | Element | Usage |
|----------|---------|-------|
| pixilart-sprite (10).png | Chive plant | Crop animation |
| pixil-frame-0 - 2023-12-11T105420.784.png | Player character | Main sprite |
| boycat_walkcycle.png | Boy character | NPC sprite |
| michaelfall.png | Michael character | NPC sprite |
| michaelfalldamage.png | Michael (damaged) | Story variant |
| pixilart-frames/michaelwalkdown.png | Michael walking | Cutscene animation |
| riva.png, riva2.png | Riva character | NPC sprites |
| grand-cultist-walk_forward.png | Cultist enemy | Enemy sprite |

### Crops & Plants:
| PNG File | Element |
|----------|---------|
| potato sprites.png | Potato growth stages (5 frames) |
| wheat.tres | Wheat crop resource |
| pixil-frame-0 - 2024-01-16T123135.698.png | Redbaneberry icon |
| pixil-frame-0 - 2024-01-16T124429.661.png | Chive icon |
| pixil-frame-0 - 2024-01-16T170843.375.png | Sorrel icon |
| pixil-frame-0 - 2024-01-22T145636.059.png | Pinecone icon |
| assets/pixil-frame-0 - 2024-01-16T112753.850.png | Elderberry icon |

### Buildings & Architecture:
| PNG File | Element |
|----------|---------|
| pixil-frame-0 - 2024-02-03T182612.576.png | House type 1 (Generic) |
| lunar_propaganda_1.png | Mayor's house (special) |
| pixil-frame-0 - 2024-02-13T084115.909.png | House variant 2 |
| pixilart-drawing.png | Main town tileset |
| stone_bricks.png | Wall texture |
| road_pieces_1.png | Road elements |
| shelburne_town_road.png | Town road |
| main_road_curve.png | Road intersection |
| road_intersection_x4.png | 4-way intersection |
| road_intersection_shelburne.png | Town intersection |

### Terrain & Environment:
| PNG File | Element |
|----------|---------|
| grass_2.png, grass_3.png, grass_4.png | Grass variants |
| water_tiles_3.png | Water terrain |
| spawn_lake.png | Starting area lake |
| pixil-frame-0 (31).png, (37).png | Environmental sprites |

### UI & Icons:
| PNG File | Element |
|----------|---------|
| assets/iron_axe.png | Axe tool icon |
| assets/Item Assets/placeables/construction_table.png | Building table icon |
| bad_economy.png | Low demand indicator |
| decent_economy.png | Neutral demand indicator |
| good_economy.png | High demand indicator |
| inventory/marker_clicked.png | Map marker (selected) |
| inventory/marker_notclicked.png | Map marker (unselected) |

### Shaders & Effects:
| File | Effect |
|------|--------|
| pause_menu.gdshader | CRT scanlines, distortion, vignette |
| color_depth.gdshader | Color depth reduction |
| vibranto.gdshader | Color vibrance/saturation |
| highlow.gdshader | Brightness/contrast |
| playboy.gdshader | Special shader effect |

### Audio Files:
| File | Usage |
|------|-------|
| Guitar_song_.m4a | Background music |
| pokemon_town_ahh - Copy.mp3 | Town ambience |
| pokemon_town_ahh - Copy.wav | Town ambience (WAV) |
| Zea_first_cutscene.mp3 | Story cutscene audio |
| Zea_first_cutscene.wav | Story cutscene audio (WAV) |
| mainmenuahh song.mp3 | Main menu music |
| Main_menu_.wav | Main menu sound effect |
| New_Project_2 (1).wav | Sound effect |
| x2mate.com - Rody rich -ricch forever Instrumental (128 kbps).mp3 | Background track |
| x2mate.com - eek! but every eek is replaced with ahh (128 kbps).mp3 | Meme audio |
| lessee.mp3 | Sound effect |

---

## Zone Structure & World Organization

### **Main World Zones:**

#### **Zone 1: Spawn Area**
- **Scene:** world_2.tscn
- **Type:** Starting location
- **Features:**
  - Opening cutscene with dramatic camera path
  - Introduces game world
  - Basic terrain and obstacles
  - Entry point for player

#### **Zone 2: Shelburne Town**
- **Scene:** shelburne.tscn
- **Type:** Main settlement/trading hub
- **Locations:**
  - Town center (shelburne_centrum)
  - Streets and roads
  - Phillip's Merchant shop
  - Leo's Alcohol Shop (scenes/leo_alcohol_shop.tscn)
  - Multiple houses (types 1, 2, 3)
  - Zea's house (story location)
  - Town mountain backdrop
  - North mountain
  - Bridge to other areas
- **NPCs:** Phillip (merchant), Zea (story), others
- **Activities:** Trading, story progression

#### **Zone 3: Mountain Areas**
- **Mount Crag (mountcrag.tscn)**
  - Terrain formation
  - Resource gathering
- **Top of Mt. Crag (top_of_mt_crag.tscn)**
  - Story event location
  - Emits "cutscene_over" signal
  - Major plot point

#### **Zone 4: Forest Areas**
- **Shelburne Forest**
  - Information marker in map
  - Resource gathering location
  - Tree harvesting
- **Bush/Vegetation Areas**
  - Cranberry bushes
  - Spruce trees
  - Various flora

#### **Zone 5: Underground**
- **Cave (cave.tscn)**
  - Stalagmite resources
  - Underground exploration
  - Flint gathering

#### **Zone 6: Sandbox/Testing Area**
- **Purpose:** Open-ended building/testing
- **Features:** Unrestricted placement

---

## NPC Locations & Dialogue

### **Major NPCs:**

#### **Zea**
- **Location:** Zea's house (shelburne.tscn)
- **Story Role:** Main character quest giver
- **Dialogues:**
  - `second_dialogue_zea.tscn` - Initial encounter
  - `third_zea_dialogue.tscn` - Mid-story interaction
  - `fourth_zea_dialogue.tscn` - Advanced dialogue
  - Inside house cutscene with unknown man
- **House Interior:** inside_zea_house.tscn
- **Mechanics:** Triggers house entry, cutscenes, story progression

#### **Phillip (Merchant)**
- **Location:** Shelburne town center
- **Role:** Primary trader/economy system
- **First Interaction:** philip_first_dialogue.tscn
- **Trades:** All 7 categories of goods
- **Economy:** Dynamic demand-based pricing
- **Shop Items:**
  - Red Baneberry
  - Chives
  - Elderberry
  - Pinecone
  - Sorrel
  - Iron Axe
  - Building Table
  - Additional slots for expansions

#### **Mark**
- **Dialogue:** mark_dialogue.tscn
- **Role:** Secondary NPC

#### **Unknown Man**
- **Location:** inside_zea_house.tscn
- **Role:** Story character
- **Dialogue:** unknown_dialogue.tscn
- **Appearance:** First cutscene event

#### **Henry**
- **Scene:** henry.tscn
- **Role:** Named character (details in scene)

#### **Boy Character**
- **Scene:** boykisser.tscn
- **Sprite:** boycat_walkcycle.png

#### **NPC with Quest**
- **Scene:** npc_quest.tscn
- **Role:** Quest-giving entity

#### **Leo**
- **Location:** leo_alcohol_shop.tscn (scenes/)
- **Role:** Shop owner

#### **Michael**
- **Sprites:** michaelfall.png, michaelfalldamage.png
- **Role:** Story/enemy character

---

## Player Mechanics & Interaction

### **Player Script Reference (character_body_2d.gd):**
- **Base Speed:** 100 units/second
- **Direction Tracking:** Tracks current direction (left, right, up, down)
- **Type:** CharacterBody2D with physics
- **Movement:** Velocity-based with physics processing

### **Inventory System:**
- **Script:** inventory.gd
- **Classes:** InvItem (inventory item definition)
- **Slots:** Hotbar + main inventory
- **UI Components:**
  - inv_improved_ui.tscn - Main inventory
  - inv_hotbar.tscn - Quick access
  - Inv_slot.gd - Individual slot behavior

### **Building System:**
- **Script:** build_placable.gd
- **Mechanics:**
  - Place structures (fences, log seats, etc.)
  - Building table required for crafting
  - Placeable variants of crops
  - Visual placement feedback

### **Interaction Keys:**
- **E Key:** Pick up items, enter buildings, interact with NPCs
- **N Key:** Open shop/merchant UI
- **M Key:** Open map
- **Escape:** Close menus
- **Mouse Scroll:** Map zoom

---

## Game Systems Overview

### **Day/Night System:**
- **Script:** day_and_night.gd
- **Scene:** day_and_night.tscn
- **Features:** Dynamic lighting cycle

### **Audio Management:**
- **pause_menu.gd** - Audio settings control
- **audio_settings.gd** - Advanced audio options
- **Multiple audio tracks** for ambience, music, SFX

### **Camera System:**
- **Player camera:** Integrated CharacterBody2D camera
- **Cutscene cameras:** Path-following for story sequences
- **Zoom capability:** Via scroll wheel in menu

### **Save System:**
- **SaveData:** gamesaves class
- **Persistence:** Player position, story state

### **Global Systems:**
- **meta_information.gd** - Game state tracking
- **global_cache.gd** - Cached data
- **LoadManager.gd** - Save/load functionality

---

## Technical Architecture

### **Scene Loading Pattern:**
Most complex scenes use `preload()` for runtime instantiation:
```gdscript
var instance_file = preload("res://scene_name.tscn")
var instance = instance_file.instantiate()
add_child(instance)
```

### **Script Organization:**
- GDScript (`.gd`) files for logic
- Scene files (`.tscn`) for structure
- Resource files (`.tres`) for item definitions
- Shaders (`.gdshader`) for visual effects

### **Signal/Event System:**
Extensive use of Godot signals for:
- Dialogue progression
- Economy updates
- Story events
- Player actions
- NPC interactions

### **Resource Management:**
- `.tres` files for game items/data
- Textures as `Texture2D` resources
- Atlas textures for animated sprites
- Animation libraries for complex sequences

---

## Known Issues & Incomplete Systems

1. **Inventory System** - Basic structure, full UI implementation in progress
2. **Crafting Recipes** - Defined in UI, not in script logic
3. **Quest System** - Framework present, full implementation ongoing
4. **Enemy System** - Test scenes present, not fully integrated
5. **Multiple Dialogue Variants** - Story branching framework ready

---

## File Statistics

- **Total .tscn files:** 93
- **Total .gd files:** 81
- **PNG textures:** 200+ assets
- **Audio files:** 8+ tracks
- **Shader files:** 5 custom shaders
- **Resource files:** 15+ .tres definitions

---

## Conclusion

Croptopia is a richly detailed farming/exploration game with:
- Multiple interconnected world zones
- Dynamic economy system with NPC traders
- Collectible crops and resources
- Story progression through cutscenes and dialogue
- Building/placement mechanics
- Complete UI system for inventory, crafting, and menus
- Professional audio/visual polish

The scene hierarchy demonstrates good separation of concerns with reusable components (house types, NPCs, UI elements) and clear data flow through signals and scripts.
