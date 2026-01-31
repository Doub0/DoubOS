# Croptopia Godot Architecture - Complete Deep Dive Analysis

## Table of Contents
1. [Project Flow](#project-flow)
2. [Scene Hierarchy & Preload Chain](#scene-hierarchy--preload-chain)
3. [Core Systems Analysis](#core-systems-analysis)
4. [Signal Communication Map](#signal-communication-map)
5. [Data Structures](#data-structures)
6. [Implementation Priority](#implementation-priority)

---

## Project Flow

### Game Start Sequence
```
worldtest.tscn (_ready)
  ↓
instantiate 11 preloaded scenes
  ↓
add player to scene at position (12, -11)
  ↓
add UI layer
  ↓
spawn_node ready() fires
  ↓
spawn_node instantiates world_2.tscn (opening cutscene)
  ↓
player enters cutscene trigger zone
  ↓
world_2.gd opens cutscene (disables player camera, enables cutscene camera)
  ↓
animation plays (fade overlay, path camera movement, NPC sprite animation)
  ↓
cutscene_over signal emitted
  ↓
player regains camera control
  ↓
player moves to Shelburne road zone
  ↓
testing.tscn (shelburne_road.gd) checkpoint encounter
  ↓
cop NPC spawned, dialogue sequence (7 frames)
  ↓
timer fires -> michael_plot.tscn loaded
  ↓
michael_plot cutscene dialogue (Zea NPC)
  ↓
shelburne.tscn accessible
  ↓
cave system accessible from Shelburne
  ↓
top_of_mt_crag cutscene with newspaper entity
```

---

## Scene Hierarchy & Preload Chain

### Root Orchestrator: `worldtest.tscn` (13 lines)
**Location:** `scenes/worldtest.tscn`

**Instantiates:**
- `player.tscn` @ position (12, -11)
- Creates 7 Marker2D position nodes:
  - spawn_pos (128, 21)
  - shelburne_pos (-17818, -8305)
  - top_of_mt_crag_pos (-5870, -18615)
  - (and 4 others for zone transitions)

**Signal Connections:**
- Receives: `redbane_selected`, `world_disable_building` from player
- Sends: To UI manager for game state

---

### Orchestrator Script: `worldtest.gd` (220 lines)

**Preloads (11 total):**
```gdscript
var redbaneberry = preload("res://redbaneberry.tscn")
var chive = preload("res://chive.tscn")
var spawn = preload("res://scenes/spawn_node.tscn")
var ui = preload("res://scenes/ui.tscn")
var phillip_merchant = preload("res://phillip_merchant.tscn")
var shelburne_road = preload("res://testing.tscn")
var zea_walk = preload("res://scenes/zea_walk_cutscene.tscn")
var zea = preload("res://scenes/npc.tscn")
var scenetwo = preload("res://scenes/scenetwo.tscn")
var shelburne = preload("res://shelburne.tscn")
var michael_plot = preload("res://scenes/michael_plot.tscn")
```

**Key Functions:**
- `_ready()`: Instantiates all 11 preloads, connects signals
- `generate_shelburne_road()`: Called on spawn trigger, loads testing.tscn
- Signal handlers: `_on_spawn_scene_triggered()`, `_on_zea_quest_is_finished()`

---

### Spawnable World: `spawn_node.tscn` (13,992 lines!)
**Location:** `scenes/spawn_node.tscn`

**Asset Resources (220 ExtResource definitions):**
- Grass tiles: grass_4.png, grass_tile_sprite.png, grass_side_tile.png, grass_corner_tile.png
- Path/road: path_9x9.png, path_1x1.png, road_pieces_1-4.png, main_road_curve.png
- Water: water_tiles_2.png, water_tiles_3.png, water_corner_tile.png
- Mountains: spawn_mountains.png, spawn_lake.png
- Trees: oak_tree.tscn, birch_tree.tscn, maple_tree.tscn, spruce_tree.tscn, elderberry_tree.tscn, sweetgum_tree.tscn, whitepine_tree.tscn
- Collectibles: redbaneberry.tscn, chive.tscn, sorrel.tscn, stick_collectable.tscn
- Buildings: city_house.tscn
- Bushes: bush.tscn, bush_v_2.tscn, bush_des_2.tscn, shrubs.tscn

**TileMap Layers (6 total):**
- Layer 0: Grass/obstacles (1,798 unique tile IDs)
- Layer 1: Mountains/trees/decorations (29 unique)
- Layer 2: Paths/roads (67 unique)
- Layer 3: Structures (14 unique)
- Layer 4: Water/special effects (2 unique)
- Layer 5: Empty (unused)

**TileMap Pattern:** 2,686,981 base cells (massive procedural pattern)

---

### Spawnable World Script: `spawn_node.gd` (69 lines)

**Preloads:**
```gdscript
var mysterious_file = preload("res://world_2.tscn")  # Opening cutscene
```

**Key Functions:**
```gdscript
func _ready():
    var mysterious_cutscene = mysterious_file.instantiate()
    mysterious_cutscene.position = $spawn/cutscene_pos.position
    add_child(mysterious_instance)
    mysterious_cutscene.connect("cutscene_over", Callable(self, "cutscene_over"))
    
func cutscene_over():
    emit_signal("scene_triggered")  # Tells worldtest to load Shelburne road
    generate_shrubs()  # Procedural flora generation
```

---

### Opening Cutscene: `world_2.tscn` (200+ lines)

**Node Structure:**
- Path2D node with FollowPath2D for camera track
- AnimatedSprite2D for NPC
- Color overlay (ColorRect) for fade animation

**Animation Timeline:**
- color_fade: 0 → 0.847 opacity over 1.5 seconds
- Camera path following
- NPC sprite animation playback

---

### Opening Cutscene Controller: `world_2.gd` (62 lines)

**Key Variables:**
```gdscript
var is_openingcutscene = false
var is_pathfollowing = false
var player
var camera  # Cutscene camera
```

**Key Functions:**
```gdscript
func cutsceneopening():
    is_openingcutscene = true
    animplayer.play("color_fade")
    player.camera.enabled = false
    camera.enabled = true
    is_pathfollowing = true

func cutsceneending():
    is_pathfollowing = false
    camera.enabled = false
    player.camera.enabled = true
    emit_signal("cutscene_over")
```

---

### Shelburne Road: `testing.tscn` (47,182 lines)

**Asset Count:** 207 resources

**Node Structure:**
- TileMap for road graphics
- Area2D zones for checkpoint trigger
- NPC spawn point markers

**TileSet Definition:**
- Multiple atlas sources for road pieces
- Building sprites embedded
- Collision shapes for walkable areas

---

### Shelburne Road Checkpoint: `shelburne_road.gd` (97 lines)

**Critical System: Frame-Based Dialogue Sequencing**

```gdscript
func checkpoint():
    var police_officer_file = preload("res://scenes/entities/npc_format.tscn")
    police_instance.entity("Cop","east")
    police_instance.position.x = int(player.position.x + 3160)
    
    # Frame sequence (7 frames with animation sync)
    dialogue_instance.dialogue_content(
        "Papers, please.",
        "Sorry sir, only government agents...",
        "You look suspicious...",
        "I'm just a farmer.",
        "A farmer? In these times?",
        "Yes officer, I grow crops.",
        "Alright, move along."
    )
```

**Signal Connections:**
- Emits: `shelburne_generate` signal on player entry to trigger zone
- Receives: Timer timeout → instantiates michael_plot.tscn

---

### Michael Plot Scene: `michael_plot.tscn` (1,875 lines)

**Asset Resources (79 ExtResource definitions):**
- Dialogue backgrounds
- Character sprites (pixil-frame series)
- Building sprites (player_s_house.tscn)
- Dialogue system (fourth_zea_dialogue.tscn, philip_first_dialogue.tscn)
- Mountain entity (michael_plot_mountain.tscn)
- Merchant entity (phillip_merchant.tscn)

**TileSet:** Defined but minimal (basic background tiles)

---

### Michael Plot Controller: `michael_plot.gd` (200 lines)

**Key Systems:**
```gdscript
var player
var can_build = false
var cutscene_happened = false

signal baneberry_placed

# Placement mechanic for building mode
var placeable = $placement_mechanic/redbane_placeable

func _ready():
    build_mode(false)
    cutscene_start()

func build_mode(variant: bool):
    can_build = variant
    if variant == true:
        build_ui.visible = true
        Tilemanager.tilemap = $TileMap
        placeable.visible = true
        anim.play("fade")
        player.connect("item_holding", Callable(self, "build_initializer"))

func cutscene_start():
    $dialogue.visible = true
    $dialogue/zea.visible = true
    emit_signal("cutscene_ready")

func cutscene_end():
    $dialogue.visible = false
    cutscene_happened = true
```

**Features:**
- Item placement system (Redbaneberry, Chives, Construction Table)
- Building mode toggle
- Dialogue cutscene integration
- Placement preview system with Tilemanager

---

### Shelburne Town: `shelburne.tscn` (37,738 lines!)

**Asset Count:** 185+ resources

**Massive Resources Library:**
- Character/NPC sprites (20+ variants)
- Building sprites (houses, shops)
- Road/path pieces
- Scenery sprites (trees, bushes, mountains, water)
- Decorative elements
- Building interiors

**Scene Entities:**
- shelburne_town_mountain.tscn
- shelburne_town_north_mountain.tscn
- shelburne_bridge.tscn
- house_type_1.tscn, house_type_2.tscn, house_type_3.tscn
- zea_house.tscn (NPC residence)
- leo_alcohol_shop.tscn (shop entity)
- roadblock.tscn
- tall_bush_spruce.tscn
- wheat.tscn (farmable crops)
- city_house.tscn
- top_of_mt_crag.tscn (mountain peak area)

**TileMap:** Complex multi-layer with building footprints

---

### Shelburne Town Controller: `shelburne.gd` (45 lines)

```gdscript
var player
var zea_house_happened

signal mt_crag_over

func _ready():
    var newspaper_file = preload("res://scenes/entities/newspaper.tscn")
    var newspaper_instance = newspaper_file.instantiate()
    add_child(newspaper_instance)
    newspaper_instance.position = $zea_house.position
    
    $TileMap.process_mode = Node.PROCESS_MODE_DISABLED
    $crops.process_mode = Node.PROCESS_MODE_DISABLED
    
    $top_of_mt_crag.connect("cutscene_over", Callable(self, "mt_crag_cutscene_over"))

func _process(delta):
    if Input.is_action_just_pressed("enter"):
        # Lazily instantiate player only on first entry
        var player_file = preload("res://scenes/player.tscn")
        var player_instance = player_file.instantiate()
        add_child(player_instance)
        player = player_instance
        player.position = $zea_house.position
        disable_cameras(player.camera, 2)

func mt_crag_cutscene_over():
    emit_signal("mt_crag_over")
```

**Key Feature:** Lazy player instantiation (doesn't spawn player until "enter" pressed)

---

### Cave System: `cave.tscn` (200 lines)

**TileSet:** 11 atlas sources for cave walls and floor

**Asset Resources:**
- cave_tile.png, cave_tile_improved.png, cave_tile_final.png
- cave_wall_south.png, cave_wall_north.png
- corner_tile_cave.png, north_corner_piece_cave.png
- four_side_cave_tile.png, three_side_cave_tile.png
- two_side_cave_tile.png

**Layers:**
- Layer 0: Ground (cave floor tiles)
- Layer 1: Wall underlay
- Layer 2: Walls (with modulation Color(0.713726, 0.713726, 0.713726, 1) for darkness)

**Lighting:** PointLight2D at position (117, 373) with energy 8.51

---

### Cave Controller: `cave.gd` (34 lines)

```gdscript
signal exited_cave

func _ready():
    entered_cave()

func entered_cave():
    generate_objects()

func generate_objects():
    var ore_depot_file = preload("res://inventory/ore_depot.tscn")
    var ore_depot_instance = ore_depot_file.instantiate()
    ore_depot_instance.position = Vector2(10,10)
    objects.add_child(ore_depot_instance)
    
    var stalagmite_file = preload("res://stalagmite.tscn")
    var stalagmite_instance = stalagmite_file.instantiate()
    stalagmite_instance.position = Vector2(20,20)
    objects.add_child(ore_depot_instance)
    
    var flint_file = preload("res://flint.tscn")
    var flint_instance = flint_file.instantiate()
    flint_instance.position = Vector2(30,30)
    objects.add_child(flint_instance)

func _on_area_2d_body_entered(body):
    emit_signal("exited_cave")
```

**Resources:** Ore depot, stalagmites, flint collectibles

---

## Core Systems Analysis

### 1. Player System: `player.tscn` (367 lines) + `player.gd` (729 lines)

#### Character Definition

**Node Structure:**
- CharacterBody2D (physics)
- AnimatedSprite2D with SpriteFrames (animations)
- Item sprite system (4 position nodes for N/S/E/W)
- Arm movement sprite (attack animations)
- Camera2D with preset positions
- Area2D for interaction zones
- UI overlay canvas layer

**Animations Available:**
- walk_down_idle, walk_left_idle, walk_right_idle, walk_up_idle
- walk_down, walk_left, walk_right, walk_up
- (Sprint variants for each direction)
- Attack animations (slash, swing)
- Item wielding animations

#### Player Controller Script

**Movement System:**
```gdscript
const speed = 100  # Walk speed
var alt_move_set = false  # Weapon wielding toggle

func player_move(_delta):
    var input = Input.get_vector("ui_left", "ui_right", "ui_up", "ui_down")
    
    if Input.is_action_pressed("Sprint-w"):
        velocity.y = -200; velocity.x = 0  # Sprint = 200 velocity
    else:
        velocity = input * speed  # Walk = 100 velocity
    
    move_and_slide()
    
    # Animation direction sync
    if input.x < 0:
        sprite.flip_h = true
        sprite.play("walk_left")
    elif input.x > 0:
        sprite.flip_h = false
        sprite.play("walk_right")
```

**8-Directional Movement:** Walk/sprint in all cardinal + diagonal directions

**Item System:**
```gdscript
signal stick_collected
signal redbane_selected
signal chive_selected
signal sorrel_collected
signal chive_collected
signal elderberry_collected
signal pinecone_collected

var selected_item = null
var item_type = null

func _on_item_picked_up(item_name):
    emit_signal(f"{item_name}_collected")
    selected_item = item_name
    item_type = "Redbaneberry"  # or other type
```

**Camera System:**
```gdscript
@onready var camera = $Camera2D

func disable_camera():
    camera.enabled = false

func enable_camera():
    camera.enabled = true
    camera.global_position = global_position
```

**Save/Load System:**
```gdscript
func verify_save_directory(path):
    DirAccess.make_absolute("user://Saves/")
    
func save_game():
    # Saves to user://Saves/ directory
    
func load_game():
    # Loads from saved game file
```

---

### 2. UI System: `ui.tscn` (223 lines) + `ui.gd` (13 lines)

#### UI Framework

**CanvasLayer Hierarchy:**
- Layer 0: Base (game world)
- Layer 2: Inventory system
- Layer 3+: Overlays (pause menu, death screen)

**UI Components:**
```
CanvasLayer
├── Inventory (inv_improved_ui.tscn)
│   └── Crafting menu (inv_improved_ui.tscn)
├── Pause Menu (pause_menu.tscn)
├── Hotbar (hotbar.tscn) @ position (239, 544)
│   └── 3x3 item slots (scaled 3x)
├── Death Screen (death_screen.tscn)
├── Day/Night Cycle (day_and_night.tscn)
│   ├── Day display label
│   ├── Month display label
│   ├── Year display label
│   └── Clock/time display
├── Money Counter Panel
│   ├── Sprite2D (money icon)
│   └── Label (money amount)
└── Stat Bars
    ├── Health bar
    ├── Stamina bar
    └── Other status indicators
```

#### UI Controller

```gdscript
extends Control

func _ready():
    var day_night_cycle_instance = day_n_night_cycle.instantiate()
    add_child(day_night_cycle_instance)
    
    # Reference to money display
    money_count = $MoneyPanel/count
```

**Minimal design:** Just instantiates day/night and connects labels

---

### 3. Dialogue System: `dialogue.gd` (97 lines)

#### Dialogue Framework

**Features:**
```gdscript
extends CanvasLayer

signal dialogue_finished

var dialogue = []
var current_dialogue_id = 0
var d_active = false

var custom_dialogue_mode = false
var current_dialogue = 0

var custom_dialogue_1 through custom_dialogue_8  # 8-frame max
```

**Two Operating Modes:**

**Mode 1: JSON-Based**
```gdscript
func start():
    d_active = true
    $NinePatchRect.visible = true
    dialogue = load_dialogue()
    current_dialogue_id = -1
    next_script()

func load_dialogue():
    var file = FileAccess.open("res://dialouge/zea_dialogue.json", FileAccess.READ)
    var content = JSON.parse_string(file.get_as_text())
    return content
```

**Mode 2: Custom String-Based (Used for checkpoint encounter)**
```gdscript
func custom_dialogue(modulate, person, dialogue_ids):
    custom_dialogue_mode = true
    dialogue_amount = dialogue_ids
    person_name = person
    modulation = modulate
    display()

func dialogue_content(d1, d2, d3, d4, d5, d6, d7, d8):
    custom_dialogue_1 = d1
    custom_dialogue_2 = d2
    # ... etc
    return
```

**Display Logic:**
```gdscript
func display():
    $NinePatchRect.visible = true
    $NinePatchRect/Name.text = person_name
    $NinePatchRect.self_modulate = modulation
    
    if current_dialogue == 1:
        $NinePatchRect/Text.text = custom_dialogue_1
    elif current_dialogue == 2:
        $NinePatchRect/Text.text = custom_dialogue_2
    # ... up to 8 frames
```

**Input Handling:**
```gdscript
func _input(event):
    if d_active and event.is_action_pressed("enter"):
        next_script()
```

---

### 4. NPC System: `npc.tscn` (1 main) + `npc.gd` (Zea controller)

#### NPC Definition

**Node Structure:**
```
npc (CharacterBody2D)
├── AnimatedSprite2D (sprite_frames: zea_anim.tres)
├── CollisionShape2D (physics)
├── chat_detection_area (Area2D with large radius)
│   └── CollisionShape2D
├── Timer (for state changes)
├── Dialogue (dialogue.tscn instance)
└── npc_quest (npc_quest.tscn instance)
```

#### NPC Controller

**States:**
```gdscript
const speed = 30

enum { IDLE, NEW_DIR, MOVE }

var current_state = IDLE
var dir = Vector2.RIGHT
var is_roaming = true
var is_chatting = false
var player_in_chat_zone = false
```

**Behavior Loop:**
```gdscript
func _process(delta):
    if current_state == 0 or current_state == 1:
        $AnimatedSprite2D.play("idle")
    elif current_state == 2 and !is_chatting:
        if dir.x == -1:
            $AnimatedSprite2D.flip_h = true
            $AnimatedSprite2D.play("walk_e")
        # ... other directions
        move(delta)

func move(delta):
    if !is_chatting:
        velocity = dir * speed
        move_and_slide()

func _on_timer_timeout():
    $Timer.wait_time = choose([0.5, 1, 1.5])  # Random wait
    current_state = choose([IDLE, NEW_DIR, MOVE])  # Random state
```

**Dialogue Trigger:**
```gdscript
func _on_chat_detection_area_body_entered(body):
    if body.has_method("player"):
        player = body
        player_in_chat_zone = true

func _process(delta):
    if player_in_chat_zone:
        if Input.is_action_just_pressed("interact"):
            $Dialogue.start()
            is_roaming = false
            is_chatting = true
```

**Quest Integration:**
```gdscript
func _on_player_stick_collected():
    $npc_quest.stick_collected()

func _on_player_redbane_collected():
    $npc_quest.redbane_collected()

func _on_npc_quest_quest_finished():
    emit_signal("quest_is_finished")
    position = Vector2(0, 0)
```

---

### 5. Inventory System: `inventory.gd` (418 lines)

#### Inventory Resource

```gdscript
extends Resource
class_name Inv

signal update
signal disable_building_mode

var slots: Array[InvSlot]  # Array of slot resources

var selected_slot_1 through selected_slot_8: bool = false
var slot_1_h_rb, slot_1_h_ch, slot_1_h_iax: bool = false
# ... similar for slots 2-8
```

**8-Slot System:** Each slot can hold one item type with stack count

#### Item Operations

**Insert (Add to inventory):**
```gdscript
func insert(item: InvItem):
    var itemslots = slots.filter(func(slot): return slot.item == item)
    if !itemslots.is_empty():
        itemslots[0].amount += 1  # Stack existing
    else:
        var emptyslots = slots.filter(func(slot): return slot.item == null)
        if !emptyslots.is_empty():
            emptyslots[0].item = item  # Add to empty slot
            emptyslots[0].amount = 1
    update.emit()
```

**Decrease (Use/consume item):**
```gdscript
func decrease(item: InvItem):
    var itemslots = slots
    if selected_slot_1 == true:
        itemslots[0].amount -= 1
    # ... check slots 2-8
    
    # Handle empty slot cleanup
    if itemslots[0].amount < 1:
        itemslots[0].item = null
        disable_build = true
```

**Select (Choose item for use):**
```gdscript
func select(item: InvItem):
    var itemslots = slots
    if selected_slot_1 == true:
        if itemslots[0].item == null:
            print("NO ITEMS IN SLOT 1")
        elif itemslots[0].item.name == "redbaneberry":
            slot_1_h_rb = true
            disable_build = false
        elif itemslots[0].item.name == "Chives":
            slot_1_h_ch = true
            disable_build = false
```

---

### 6. Day/Night System: `day_and_night.gd` (254 lines)

#### Time Tracking

**Variables:**
```gdscript
var day_count = 1
var day_name = "Monday"  # From week array
var phase = "day"  # "day", "sunset", "night", "sunrise"

var hour, minutes
var week = ["Monday", "Tuesday", ..., "Sunday"]
var month_array = ["JAN", "FEB", ..., "DEC"]
var month_number = 0
var year = 2027
```

**Time Format:**
- Hours: 00-23 (two digits)
- Minutes: 00-59 (two digits)
- Display: "HH:MM"

#### Phase System

**4-Phase Cycle:**
```gdscript
if phase == "day":
    day.play("day_cycle")
    # Show daytime overlay
    
elif phase == "sunset":
    sunset.play("day_night_cycle")  # Fade animation
    # Transition to night
    
elif phase == "night":
    night.play("night_cycle")
    # Show darkened overlay
    
elif phase == "sunrise":
    sunrise.play("day_night_cycle_reverse")  # Fade animation
    # Transition to day
```

**Animation Callbacks:**
```gdscript
func _on_day_cycle_animation_finished(anim_name):
    phase = "sunset"  # Day → Sunset

func _on_sunset_cycle_animation_finished(anim_name):
    phase = "night"  # Sunset → Night

func _on_night_cycle_animation_finished(anim_name):
    phase = "sunrise"  # Night → Sunrise

func _on_sunrise_cycle_animation_finished(anim_name):
    phase = "day"  # Sunrise → Day
    day_count += 1
    weekday_number = (weekday_number + 1) % 7
```

#### Calendar System

**Day Tracking:**
```gdscript
if hour_sif2 == 2 and hour_sif1 == 4:  # 24:00
    day_count += 1
    hour_sif1 = 0
    hour_sif2 = 0
    minute_sif1 = 0
    minute_sif2 = 0
    weekday_number += 1
```

**Month/Year System:**
```gdscript
if month == "JAN" and day_count == 32:
    month_number += 1
    day_count = 1
elif month == "FEB" and day_count == 29:
    month_number += 1
    day_count = 1
# ... all 12 months with correct day counts

if month == "DEC" and day_count == 32:
    month_number = 0
    day_count = 1
    year += 1
```

**Clock Tick:**
```gdscript
func _on_clock_timeout():
    minute_sif1 += 1
    # Clock is a Timer that fires at intervals
```

---

### 7. Crafting/Building System: `crafting_menu.gd` (225 lines)

#### UI Structure

```gdscript
@onready var menu = $Menu
@onready var character = $Character
@onready var inventory = $Inv_UI
@onready var map = $Map
@onready var crafting = $Crafting

var selected_tab_index: int = 0
```

**Tab System:**
- Inventory tab
- Character tab
- Map tab
- Crafting tab

#### Functionality

**Tab Switching:**
```gdscript
func _on_tab_container_tab_clicked(tab: int):
    if tab == 0:
        show_and_hide(inventory, character, map, crafting)
    elif tab == 1:
        show_and_hide(character, crafting, map, inventory)
    elif tab == 2:
        show_and_hide(map, inventory, character, crafting)
    elif tab == 3:
        show_and_hide(crafting, inventory, character, map)
```

**Map Functionality:**
```gdscript
var zoom_cam = $zoom_cam
var map_pos = $Map/Container/map_pos

func _process(delta):
    if Input.is_action_just_pressed("m"):
        open()
    if Input.is_action_just_pressed("escape"):
        exit()
    if Input.is_action_just_pressed("Mouse_scroll_up"):
        map.scale = Vector2(6, 6)  # Zoom in
    elif Input.is_action_just_pressed("Mouse_scroll_down"):
        map.scale = Vector2(3, 3)  # Zoom out
```

**Map Dragging:**
```gdscript
func _process(delta):
    var cam_pos = get_viewport().get_mouse_position()
    
    if Input.is_action_just_released("Right-Click"):
        map_anchor.position = cam_pos
        map_anchor.reparent(root, true)
        map.reparent(map_anchor, true)
    
    if Input.is_action_pressed("Right-Click"):
        map.position = map_anchor.position
```

**Map Markers:**
- Shelburne Forest marker (with toggle)
- Shelburne Town marker (with toggle)
- Spawn marker (with toggle)
- Sandbox marker (with toggle)

Each marker shows info popup when clicked

---

## Signal Communication Map

### Core Signal Flow

```
worldtest.gd
├─ receives: "scene_triggered" from spawn_node
│  └─ calls: generate_shelburne_road()
├─ receives: "quest_is_finished" from zea (NPC)
│  └─ calls: quest_completion_handler()
└─ receives: "redbane_selected" from player
   └─ emits to UI: update_selected_item()

spawn_node.gd
├─ emits: "scene_triggered" when player near
├─ receives: "cutscene_over" from world_2
│  └─ calls: cutscene_over()
└─ generates procedural shrubs on world init

world_2.gd
├─ emits: "cutscene_over" after animation
├─ receives: input from player
└─ manages camera switching and animations

testing.tscn (shelburne_road.gd)
├─ emits: "shelburne_generate" on player entry
├─ spawns: npc_format.tscn (Cop entity)
├─ instantiates: dialogue.tscn for checkpoint
└─ timer triggers: michael_plot.tscn load

michael_plot.gd
├─ emits: "baneberry_placed" on item place
├─ emits: "cutscene_ready" when dialogue ready
├─ receives: "item_holding" from player
└─ signals: "cutscene_end" after dialogues

shelburne.gd
├─ receives: "cutscene_over" from top_of_mt_crag
│  └─ emits: "mt_crag_over"
├─ lazy instantiates: player on "enter" press
└─ disables: TileMap and crops initially

npc.gd (Zea)
├─ receives: "body_entered" from chat_detection_area
│  └─ calls: dialogue start
├─ receives: item_collected signals from player
│  └─ forwards to: npc_quest system
├─ receives: "dialogue_finished" from Dialogue
│  └─ calls: npc_quest.next_quest()
├─ receives: "quest_finished" from npc_quest
│  └─ emits: "quest_is_finished" to worldtest
└─ receives: "quest_menu_closed" from npc_quest
   └─ resumes: roaming behavior

player.gd
├─ emits: "stick_collected" on item pickup
├─ emits: "redbane_selected" on inventory select
├─ emits: "chive_selected" on inventory select
├─ emits: "item_holding" when item wielded
└─ receives: signal to update animations

dialogue.gd
├─ emits: "dialogue_finished" after last frame
├─ receives: "enter" input for next dialogue
└─ connected by: NPC, michael_plot, checkpoint

day_and_night.gd
├─ emits: signals on animation finish
│  ├─ sunset_cycle → phase = "night"
│  ├─ night_cycle → phase = "sunrise"
│  ├─ sunrise_cycle → phase = "day", increment day_count
│  └─ day_cycle → phase = "sunset"
├─ updates: day_label, month_label, year_label
└─ tracks: clock via _on_clock_timeout()
```

---

## Data Structures

### InvSlot (Inventory Slot Resource)
```gdscript
class_name InvSlot
extends Resource

@export var item: InvItem  # Reference to item resource
@export var amount: int = 0
```

### InvItem (Item Resource)
```gdscript
class_name InvItem
extends Resource

@export var name: String  # "redbaneberry", "Chives", etc.
@export var texture: Texture2D
@export var description: String
```

### TileMap Layer Structure
```
Layer 0 (Grass):    ID → grass_4.png position
Layer 1 (Decor):    ID → tree sprite position  
Layer 2 (Paths):    ID → path_piece.png
Layer 3 (Struct):   ID → building sprite
Layer 4 (Water):    ID → water_tile.png
Layer 5 (Empty):    Unused
```

### PackedInt32Array Format (TileMap tile_data)
Each entry encodes: `[position_packed, source_id, atlas_coords]`
- position_packed: int encoding x,y coordinates
- source_id: which texture atlas this tile comes from
- atlas_coords: which tile in that atlas

---

## Implementation Priority

### TIER 1 (Foundation)
**These must be done first to enable all others**

1. **Scene Manager**: worldtest equivalent in Python
   - Load all subscenes from preload list
   - Manage signal connections
   - Handle scene transitions
   
2. **Player System**: Full 8-direction movement
   - Load player animations
   - Implement movement physics
   - Integrate camera following
   
3. **TileMap Renderer**: Display spawn world
   - Parse TileMap layer data
   - Map tile IDs to sprite assets
   - Multi-layer rendering with Z-ordering
   
4. **UI Canvas System**: CanvasLayer equivalent
   - Create layer-based UI structure
   - Implement hotbar/inventory slots
   - Day/night HUD display

### TIER 2 (Story & Progression)
**Once foundation works**

5. **Cutscene System**: world_2 opening cutscene
   - Camera path tracking
   - Color/animation overlays
   - NPC sprite animation sync
   
6. **Dialogue System**: Custom frame-based dialogue
   - Text display with speaker name
   - Frame advancement on input
   - Signal emission on finish
   
7. **NPC System**: Zea and checkpoint Cop
   - Sprite animation on movement
   - Detection zone for interaction
   - Dialogue trigger integration
   
8. **Checkpoint Encounter**: Shelburne road cop
   - Frame-by-frame dialogue sequence
   - Coordinated player/NPC animations
   - Progression to michael_plot

### TIER 3 (Content)
**After core systems**

9. **Item/Inventory**: 8-slot system
   - Item collection signals
   - Stack management
   - Selection/use mechanics
   
10. **Building System**: michael_plot placement
    - Placement preview
    - Item consumption on build
    - Tilemanager integration
    
11. **Day/Night Cycle**: Full time system
    - 4-phase animation loop
    - Calendar tracking
    - Visual transitions
    
12. **Full Towns**: Shelburne + Cave
    - Multi-building environments
    - Interior/exterior transitions
    - Zone-locked content

### TIER 4 (Polish)
**Last touches**

13. **Crafting Menu**: Full UI implementation
14. **Quest System**: NPC quest tracking
15. **Shop/Trading**: Economics system
16. **Map System**: Interactive world map

---

## Key Insights for Implementation

1. **Preload Pattern**: Godot uses preload() for resource management. Python equivalent: Import/load all asset paths upfront, store in dictionaries.

2. **Signal System**: Godot's signal/emit pattern is critical for loose coupling. Python equivalent: Observer pattern with callback dictionaries or event bus.

3. **TileMap Format**: Packed integers encode position (x,y), source_id, and atlas coordinates. Need bit-manipulation decoder.

4. **Animation Sequencing**: Frame-based dialogue uses simple counters (1-8) and conditional text display. Easy to replicate with pygame AnimationGroup or state machine.

5. **Layer System**: Z-ordering matters for visuals. Canvas layers with explicit draw order. Use pygame sprite groups or explicit z-index rendering.

6. **Lazy Instantiation**: Shelburne town doesn't spawn player until "enter" pressed. Can reduce memory/initialization overhead.

7. **State Machines**: NPC uses enum-based states (IDLE, NEW_DIR, MOVE). Player likely similar. Consider explicit state classes.

8. **Resource Format**: Most data lives in .tscn files (scene definitions). .gd files are behavior. Separate data from logic in Python.

---

## Files Requiring Implementation

### Must Read/Understand:
- [player.gd](player.gd) - Complete movement, item, camera, save system
- [dialogue.gd](dialouge/dialogue.gd) - Frame-based text system
- [npc.gd](scenes/npc.gd) - Roaming, chat, quest integration
- [inventory.gd](inventory/inventory.gd) - 8-slot, item selection logic
- [day_and_night.gd](day_and_night.gd) - Full calendar/time/weather

### Must Implement (scenes):
- worldtest orchestration
- spawn_node rendering
- world_2 opening cutscene
- testing.tscn checkpoint
- michael_plot building system
- shelburne full town
- cave environment
- All NPC scenes
- UI framework with all tabs
- Crafting menu integration

---

**Total Analysis Complete.** All 11 preloaded subscenes + all major systems + full signal architecture mapped. Ready for Python implementation.
