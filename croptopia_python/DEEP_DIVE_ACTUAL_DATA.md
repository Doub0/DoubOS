# CROPTOPIA DEEP DIVE - Actual Godot Data Extraction

**Source**: `Croptopia - 02.11.25` folder (156 .tscn, 133 .gd files)  
**Method**: Direct file reading, no assumptions

**⚠️ CENTRAL DOCUMENT** - This is the ONE file for breadcrumb trail extraction. 
NO new documentation files created each time. Only this one updated continuously.

---

## 🗺️ EXACT NODE POSITIONS (from worldtest.gd)

### Scene Positions
```python
# From scenes/worldtest.gd - ACTUAL coordinates
shelburne_road = Vector2(-3200, -2949)
michael_plot = Vector2(-2845, -2985)
shelburne = Vector2(-10388, -1849)
player_spawn = Vector2(-2845, -2985)  # Same as michael_plot
```

### NPC Positions
```python
# Zea NPC instances
zea_first = Vector2(-297, -1287)
zea_walk_instance = Vector2(-297, -1287)
zea_second_instance = Vector2(-5091.517, -3156.3)

# Cop (shelburne_road.gd checkpoint cutscene)
cop_position_x = player.position.x + 3160
cop_position_y = player.position.y + 2950
cop_type = "Cop"
cop_direction = "east"
```

### Player Teleport Points
```python
# From worldtest.gd scene transitions
to_inside_zea_house = Vector2(-2845, -2789)
to_shelburne = Vector2(-4603, -1959)
world_2_opening = Vector2(-1000, 0)
scenetwo_spawn = Vector2(-5100, -3031)
```

---

## 💬 ACTUAL DIALOGUE CONTENT

### Zea First Dialogue (`zea_dialogue.json`)
```json
[
  {"name": "Zea", "text": "A new person here?"},
  {"name": "Zea", "text": "We never get those here!"},
  {"name": "Zea", "text": "Listen..."},
  {"name": "Zea", "text": "My mom is very sick unfortunatly, and we have no medicine left..."},
  {"name": "Zea", "text": "Could you help me make the medicine? I need..."},
  {"name": "Zea", "text": "20 pinecones, 5 sticks, 5 sorrel, 10 red baneberries, 10 bundles of chives, 10 clumps of elderberries."}
]
```

**Quest Items Required**:
- 20 pinecones
- 5 sticks
- 5 sorrel
- 10 red baneberries
- 10 bundles of chives
- 10 clumps of elderberries

### Zea Second Dialogue (`zea_second_dialogue.json`)
```json
[
  {"name": "Zea", "text": "Sorry Michael?"},
  {"name": "Zea", "text": "I have to go!"},
  {"name": "Zea", "text": "Promise me you stay safe"},
  {"name": "Zea", "text": "Okay?"},
  {"name": "Zea", "text": "I have to go home and make dinner, feel free to explore"}
]
```

### Mark Gray Dialogue (`mark_dialogue.json`)
```json
[
  {"name": "Mark Gray", "text": "Hello Michael"},
  {"name": "Mark Gray", "text": "Yes I know, you may be confused as to who we are"},
  {"name": "Mark Gray", "text": "I'd be confused too Michael. We may seem like cultists, and if you think that, you'd be entirely right"},
  {"name": "Mark Gray", "text": "Anyways"},
  {"name": "Mark Gray", "text": "Zea here told me about you, and we see your potential. In times like these where all farms have turned scarse, we are in big need of farmers"},
  {"name": "Mark Gray", "text": "If I was to explain the whole situation, we'd be here all day"},
  {"name": "Mark Gray", "text": "Anyways, to calm you down, let me introduce myself"},
  {"name": "Mark Gray", "text": "I'm Mark Gray. Originating from Manhattan, New York. I carry big wealth, having sponsored tons of farms the entire East Coast"},
  {"name": "Mark Gray", "text": "Recently, Urbanization Projects have threatened the development of farms, and loads of people have sold their farms to the City Builders"}
]
```

**Key Lore**:
- Mark Gray is from Manhattan, New York
- He's a wealthy farm sponsor across East Coast
- Urbanization threatens farms
- He admits they're cultists
- Farming is becoming scarce

### Philip Dialogue (`philip_first_dialogue.json`)
```json
[
  {"name": "Zea", "text": "Hi. I'm Philip"},  // NOTE: Says "Zea" but introduces as Philip
  {"name": "Zea", "text": "Let me tell you how amazed I am to finally see someone dedicate themself to farming"},
  {"name": "Zea", "text": "I will stay here with you and offer you quests."},
  {"name": "Zea", "text": "In exchange you get cash, which you can trade with me for items"},
  {"name": "Zea", "text": "Does that sound okay?"}
]
```

**Philip System**:
- Quest giver NPC
- Trades quests for cash
- Merchant (cash for items)

### Cop Checkpoint Dialogue (shelburne_road.gd)
```gdscript
// From scenes/shelburne_road.gd - ACTUAL cutscene dialogue
dialogue_content(
  "Papers, please.",
  "Sorry sir, only government agents may leave the town.",
  "The town is encircled and the outskirts are a battlefield now.",
  "", "", "", "", ""
)
custom_dialogue(Color.hex(0x00ffff), "Cop", 3)  // Cyan color, 3 dialogue lines
```

**Cop Cutscene Sequence** (7 frames):
1. Cop plays "cop_e" animation, player faces left
2. Cop plays "cop_check" animation (checking papers)
3. Player plays wield animation, newspaper sprite appears
4. Cop back to "cop_e", player idle, newspaper hidden
5. Cop continues "cop_e", next dialogue line
6. Cop continues "cop_e", next dialogue line
7. Cop deleted, dialogue deleted, player movement restored

**Newspaper Asset**: `res://assets/papers_1.png` (scale 0.3x0.3)

---

## 🎭 NPC ENTITY TYPES (from npc.gd)

### Cop Entity
```gdscript
// From npc.gd entity() function
type = "Cop"
animations:
  - "cop_e" (east/west - flip_h for west)
  - "cop_n" (north)
  - "cop_s" (south)
  - "cop_check" (checking papers animation)

body_parts_removed: [face, eyes, mouth, hat, torso, pants]
// Cop uses full-body sprite, not modular parts
```

### Soldier Entity
```gdscript
type = "Soldier"
direction = "south" only (in code)
body_parts:
  - face: "default"
  - eyes: "green_eyes"
  - mouth: "default"
  - hat: "fed_helmet_s"
  - torso: "fed_uniform_s"
  - pants: (implied)

body_removed: true  // Remove "body" AnimatedSprite2D
// Soldier uses modular sprite system
```

---

## 🎬 CUTSCENE SYSTEM (shelburne_road checkpoint)

### Cop Checkpoint Flow
```python
# Trigger: player enters scenetrans Area2D
in_cutscene = True

# 1. Spawn cop NPC
cop = npc_format.instantiate()
cop.entity("Cop", "east")
cop.position = (player.position.x + 3160, player.position.y + 2950)
cop.scale = Vector2(1, 1)

# 2. Lock player
player.anim.play("walk_left_idle")
player.cam_preset("CUTSCENE")
player.player_can_move(False, True)

# 3. Load dialogue
dialogue.dialogue_content(
  "Papers, please.",
  "Sorry sir, only government agents may leave the town.",
  "The town is encircled and the outskirts are a battlefield now."
)
dialogue.custom_dialogue(Color.CYAN, "Cop", 3)

# 4. Sequence timer (2 seconds per frame)
# Frame 1: Cop looks east, player idle left
# Frame 2: Cop checks papers
# Frame 3: Player shows newspaper item
# Frame 4-6: Dialogue progresses
# Frame 7: Cleanup, restore player control
```

---

## 📁 DIALOGUE FILE REFERENCES

### Located Files
```
dialouge/zea_dialogue.json           (6 lines - first quest)
dialouge/zea_second_dialogue.json    (5 lines - going home)
dialouge/third_zea_dialogue.json     (not yet read)
dialouge/zea_fourth_dialogue.json    (not yet read)
dialouge/mark_dialogue.json          (10 lines - cultist intro)
dialouge/philip_first_dialogue.json  (5 lines - merchant intro)
```

### Dialogue Loader Pattern
```gdscript
// From fourth_zea_dialogue.gd, mark_dialogue.gd, philip_first_dialogue.gd
extends CanvasLayer

signal dialogue_finished

var dialogue = []
var current_dialogue_id = 0

func load_dialogue():
    var file = FileAccess.open("res://dialouge/[name].json", FileAccess.READ)
    var content = JSON.parse_string(file.get_as_text())
    return content

func next_script():
    current_dialogue_id += 1
    if current_dialogue_id >= len(dialogue):
        emit_signal("dialogue_finished")
        return
    
    $NinePatchRect/Name.text = dialogue[current_dialogue_id]['name']
    $NinePatchRect/Text.text = dialogue[current_dialogue_id]['text']
```

**Input**: Press "enter" to advance dialogue

---

## 🌍 WORLD STRUCTURE (from worldtest.gd coordinates)

```
                    shelburne (-10388, -1849)
                          |
                          |
    zea_second (-5091, -3156) --- scenetwo spawn (-5100, -3031)
                          |
                          |
              shelburne_road (-3200, -2949)
                     |         \
                     |          cop checkpoint
                     |
          michael_plot (-2845, -2985)  ← player spawn
                     |
                     |
              zea_first (-297, -1287)
                     |
                     |
                world_2 (-1000, 0)
```

**Distance Calculations** (from worldtest.gd):
- Zea visibility: `(zea.position.y - player.position.y) > -300` → show
- Zea hidden: `(zea.position.y - player.position.y) < -300` → hide

---

## 🎨 CUSTOM DIALOGUE SYSTEM

### Parameters (from shelburne_road.gd)
```gdscript
dialogue_instance.custom_dialogue(
  Color.hex(0x00ffff),  // Text color (cyan for cop)
  "Cop",                // Character name
  3                     // Number of dialogue lines
)
```

### UI Components
```
NinePatchRect (dialogue box)
  ├── Name (RichTextLabel)
  ├── Text (RichTextLabel)
  └── Sprite2D (portrait?)
```

---

## 🚀 NEXT STEPS FOR PYTHON IMPLEMENTATION

### Immediate Priorities
1. **Read remaining dialogue JSONs** (third_zea, fourth_zea)
2. **Map ALL node positions** from .tscn files
3. **Extract animation frame data** for cop/soldier/NPCs
4. **Document quest system** (quest tracking, item requirements)
5. **Scene transition triggers** (Area2D collision detection)

### Missing Data to Extract
- [ ] All NPC spawn positions from .tscn files
- [ ] Complete animation sprite names (cop_e, cop_n, etc.)
- [ ] Item sprite mappings
- [ ] Complete quest system implementation
- [ ] Scene connection graph (which scenes link to which)
- [ ] Collision layer data from TileMaps
- [ ] Camera preset definitions (CUTSCENE vs NORMAL)

---

## 🎯 QUEST SYSTEM DETAILS (From npc_quest.gd)

**Quest State Variables**:
```gdscript
var quest1_active = false
var quest1_completed = false
var stick = 0
var pinecone = 0
var elderberry = 0
var chive = 0
var sorrel = 0
var redbane = 0
```

**Quest Completion Logic** (EXACT from npc_quest.gd):
```gdscript
if stick >= 10:
    if pinecone >= 20:
        if elderberry >= 10:
            if chive >= 10:
                if sorrel >= 5:
                    if redbane >= 10:
                        print("You finished the quest!")
                        quest1_active = false
                        quest1_completed = true
                        play_finish_quest_anim()
                        emit_signal("quest_finished")
```

**Complete Signal Set** (from npc_quest.gd::connect_signals()):
```gdscript
player.connect("stick_collected", Callable(self, "stick_collected"))
player.connect("pinecone_collected", Callable(self, "pinecone_collected"))
player.connect("elderberry_collected", Callable(self, "elderberry_collected"))
player.connect("sorrel_collected", Callable(self, "sorrel_collected"))
player.connect("redbane_collected", Callable(self, "redbane_collected"))
player.connect("chive_collected", Callable(self, "chive_collected"))
```

**Quest UI Elements**:
- `$quest1_ui` - Quest offer dialog
- `$no_quest` - "No quests available" message (shows 3 seconds)
- `$finished_quest` - Quest completion notification (shows 3 seconds)
- `$quest1_ui/YesButton1` → accepts quest, resets all counters
- `$quest1_ui/NoButton1` → declines quest

**Quest Signals Emitted**:
- `quest_menu_closed` - when player responds to quest offer
- `quest_finished` - when all requirements met

---

## 🏗️ BUILDING/PLACEMENT SYSTEM (From michael_plot.gd)

**Placement Mechanics**:
```gdscript
# Preloaded placeables
var redbaneberry = preload("res://redbaneberry.tscn")
var construction_table = preload("res://scenes/Placeables/construction_table.tscn")
var chives = preload("res://chive.tscn")

# Placement state
var can_build = false
var placeable_item = $placement_mechanic/redbane_placeable

# Player inventory selection
if player.selected_item == "Redbaneberry":
    placeable.process_mode = Node.PROCESS_MODE_ALWAYS
    Tilemanager.tilemap = $placement_mechanic/TileMap
    placeable.variant(player.selected_item)
    
    if Input.is_action_just_pressed("Right-Click") or Input.is_action_just_pressed("left click"):
        var redbaneberry_instance = redbaneberry.instantiate()
        add_child(redbaneberry_instance)
        redbaneberry_instance.position = $placement_mechanic/redbane_placeable.position
        emit_signal("redbane_placed")

# Same pattern for Chives
if player.selected_item == "Chive":
    # ... identical placement logic
    emit_signal("chive_placed")
```

**Build Signals**:
- `baneberry_placed`
- `chive_placed`
- `redbane_placed`

---

## 🎬 CUTSCENE CAMERA SYSTEM (From zea_walk_cutscene.tscn)

**Camera Path Following** (Path2D → PathFollow2D → Camera2D):

**First Cutscene Path**:
```
[node name="first_cutscene_follow2" type="Path2D"]
position = Vector2(7.00256, -8)

[node name="PathFollow2D" type="PathFollow2D"]
position = Vector2(0.0877401, 0)
rotates = false
loop = false

[node name="questcam" type="Camera2D"]
zoom = Vector2(3.355, 3.355)
```

**Second Cutscene Path**:
```
[node name="second_cutscene_follow2" type="Path2D"]
position = Vector2(-1000, -180)
scale = Vector2(0.995935, 1)

[node name="PathFollow2D" type="PathFollow2D"]
position = Vector2(-59.88, -175)
rotation = 3.14159  # 180 degrees
h_offset = 0.12
rotates = false
loop = false

[node name="questcam" type="Camera2D"]
zoom = Vector2(3.355, 3.355)
```

**Character Sprites in Cutscene**:
```
# Zea sprite (AnimatedSprite2D2)
position = Vector2(-16.0903, -9)
animation = "idle"
flip_h = true

# Player sprite (AnimatedSprite2D)
position = Vector2(349.498, 206.921)
animation = "walk_up_idle"
offset = Vector2(-349.498, -206.921)
flip_h = true

# Shadow sprites (Pixil-frame-0-2024-02-08t084127_840/841)
modulate = Color(0, 0, 0, 0.521569)  # Semi-transparent black
scale = Vector2(0.714286, 0.419643)
show_behind_parent = true
```

---

## 📍 EXACT MARKER POSITIONS (From worldtest.tscn)

**Teleport Markers** (Marker2D nodes):
```
sandbox_post_cutscene = Vector2(-4642, -4830)
michael_plot_pos = Vector2(-4715, -4903)
top_of_mt_crag_pos = Vector2(-5870, -18615)
shelburne_road_pos = Vector2(186, -1016)
spawn_pos = Vector2(128, 21)
shelburne_pos = Vector2(-17818, -8305)
```

**Player Starting Position**:
```
[node name="player" parent="." instance=ExtResource("5_f2y4b")]
position = Vector2(12, -11)
```

**CanvasLayer UI**:
```
[node name="Label" type="Label" parent="CanvasLayer"]
offset_right = 40.0
offset_bottom = 23.0
scale = Vector2(0.68, 0.68)
```

---

## 🎨 COMPLETE ANIMATION CATALOG (From player.gd, unique_player.gd, npc.gd)

### Player Animations

**Basic Movement** (from player.gd and unique_player.gd):
```python
# Walking animations
"walk_left"           # Left movement (flip_h = false)
"walk_left_idle"      # Idle facing left
"walk_down"           # Down movement
"walk_down_idle"      # Idle facing down (DEFAULT on _ready())
"walk_up"             # Up movement  
"walk_up_idle"        # Idle facing up

# Note: Right movement uses "walk_left" with flip_h = true
```

**Wielding Tool Animations** (from player.gd alt_move_set system):
```python
# Walking while holding axe
"wield_walk_n"        # North with tool
"wield_walk_w"        # West with tool (also used for East with flip_h)
"wield_walk_s"        # South with tool
"wield_walk_idle_s"   # Idle with tool (default pose)

# Tool position sprites (dynamically loaded):
"iron_axe_back.png"   # When walking north
"iron_axe.png"        # When walking west/east
"iron_axe_front.png"  # When walking south
```

**Arm/Tool Slash Animations** (AnimationPlayer nodes):
```python
# Arm movements
arm_movement.play("front")   # Slash animation facing down
arm_movement.play("left")    # Slash animation facing left
arm_movement.play("back")    # Slash animation facing up
arm_movement.play("right")   # Slash animation facing right

# Item slash motions
item_movement.play("slash_front")
item_movement.play("slash_left")
item_movement.play("slash_back")
item_movement.play("slash_right")
```

**Sprint Animations** (high-speed movement):
```python
# From player.gd sprint mechanics
"sprint-forward"      # Up at 200 speed
"sprint-left"         # Left at 200 speed
"sprint-backwards"    # Down at 200 speed
"sprint-right"        # Right at 200 speed

# Diagonal movement (50 speed each axis)
"up-left", "up-right", "down-left", "down-right"
```

### NPC Animations (from npc.gd)

**Generic NPC Movement**:
```python
"idle"      # Standing still (played in IDLE state)
"walk_e"    # Walking east
"walk_w"    # Walking west
"walk_n"    # Walking north
"walk_s"    # Walking south
```

**Cop/Entity-Specific Animations** (from shelburne_road.gd):
```python
"cop_e"     # Cop facing east (checkpoint cutscene frame 1)
"cop_check" # Cop checking papers animation (frame 2-6)
```

### Cutscene Character Animations (from zea_walk_cutscene.tscn)

**Zea Animations**:
```python
"idle"          # Zea standing animation
"walk_up_idle"  # Player walking up idle in cutscene
```

### Resource/Collectible Animations

**Tree States**:
```python
# Whitepine tree (whitepine_tree.gd)
"no_pinecone"   # Empty tree
"pinecone"      # Tree with pinecone

# Sweetgum tree (sweetgum_tree.gd)
"no sweetgum"   # Empty tree
"sweetgum"      # Tree with sweetgum fruit

# Wheat (wheat.gd)
"no_wheat"      # Empty wheat plant
"wheat"         # Grown wheat
```

**Sorrel Plant**:
```python
"no_sorrel"     # Empty plant
"sorrel"        # Grown sorrel
```

**Collectible Drop Animations** (AnimationPlayer):
```python
# Sweetgum collectable (sweetgum_collectable.gd)
"fallingfromtree"   # Drops from tree
"fade"              # Fades out after timeout

# Sorrel collectable (sorrel_collectable.gd)
"cutdown"           # Cut down animation
"fade"              # Fade out
```

**Stalagmite States** (stalagmite.gd):
```python
"chipped"       # Damaged state
"elongated"     # Full/regrown state
```

### World/Environment Animations

**Day/Night Cycle** (from test_enviroment.gd):
```python
"day_night_cycle"           # Sunset animation
"day_night_cycle_reverse"   # Sunrise animation
"night_cycle"               # Night time
"day_cycle"                 # Day time
```

**Cutscene Camera** (from world_2.gd):
```python
"default"       # AnimatedSprite2D default animation (Path2D follow)
"color_fade"    # Screen fade transition
```

**Top of Mt. Crag** (from top_of_mt_crag.gd):
```python
anim.play("default")   # Mountain top animation
```

### UI Animations

**Quest Transition** (from zea_walk_cutscene.tscn):
```python
quest_transition.libraries   # AnimationLibrary for quest fade effects
```

**Scene Transition** (from michael_plot.gd, worldtest scenes):
```python
# Not extracted yet - referenced in commented code
"fade_out"      # Mentioned in shelburncentrum.gd (commented)
"quest_fade"    # Mentioned in shelburncentrum.gd (commented)
```

---

## 🎮 INPUT ACTIONS (From player.gd)

**Movement Keys**:
```python
# Basic movement
"up", "left", "down", "right"   # Arrow keys or WASD

# Diagonal movement (simultaneous inputs)
"up" + "left", "up" + "right", "down" + "left", "down" + "right"

# Sprint (from unique_player.gd and player.gd)
"Sprint-w"   # Sprint forward (200 speed)
"Sprint-a"   # Sprint left (200 speed)
"Sprint-s"   # Sprint backwards (200 speed)
"Sprint-d"   # Sprint right (200 speed)
"SHIFT"      # Also triggers sprint in unique_player.gd
```

**Tool/Combat Actions**:
```python
"left click"      # Place item / swing tool
"Right-Click"     # Also used for placement
"chat"            # Enables wield mode (wields_axe = true)
```

**Inventory Hotkeys**:
```python
"1", "2", "3", "4", "5", "6", "7", "8"   # Select inventory slots
```

**System Keys**:
```python
"k"   # Save game
"l"   # Load game
```

---

## 🗺️ SCENE CONNECTION GRAPH (From worldtest.gd and spawn_node.gd)

### Scene Loading System

**Scene Trigger Pattern** (from spawn_node.gd):
```gdscript
signal scene_triggered   # Emitted when player enters Area2D

func _on_player_detection_body_entered(body):
    if body.has_method("player"):
        emit_signal("scene_triggered")
```

**Main Scene Orchestration** (worldtest.gd connections):
```gdscript
# Spawn node connection
spawn.connect("scene_triggered", Callable(self, "generate_shelburne_road"))

# Scene loading sequence
func generate_shelburne_road():
    if !self.has_node("shelburnroad"):
        var shelburne_road_file = preload("res://testing.tscn")
        var shelburne_road_instance = shelburne_road_file.instantiate()
        shelburne_road_instance.position = Vector2(-3200,-2949)
        add_child(shelburne_road_instance)
        shelburne_road_instance.connect("shelburne_generate", Callable(self, "generate_shelburne"))
        shelburne_road = shelburne_road_instance
        shelburne_road_instance.player = $player
        generate_zea()   # Triggers Zea NPC generation

# Shelburne town generation
func generate_shelburne():
    if !self.has_node("shelburne"):
        var shelburne_file = preload("res://shelburne.tscn")
        var shelburne_instance = shelburne_file.instantiate()
        add_child(shelburne_instance)
        shelburne = shelburne_instance
        shelburne.position = Vector2(-10388,-1849)
        shelburne_instance.connect("mt_crag_over", Callable(self, "mt_crag_cutscene_over"))

# Michael's plot generation
func generate_michael_plot():
    if !self.has_node("michael_plot"):
        var michael_plot_file = preload("res://scenes/michael_plot.tscn")
        var michael_plot_instance = michael_plot_file.instantiate()
        add_child(michael_plot_instance)
        michael_plot = michael_plot_instance
        michael_plot.position = Vector2(-2845,-2985)

# Zea NPC generation
func generate_zea():
    var zea_file = preload("res://scenes/npc.tscn")
    var zea_instance = zea_file.instantiate()
    add_child(zea_instance)
    zea = zea_instance
    zea.connect("quest_is_finished", Callable(self, "_on_npc_quest_is_finished"))
    zea.position = Vector2(-297,-1287)
    zea.z_index = 2
```

### Scene Dependency Chain

**Loading Sequence**:
```
1. spawn_node.tscn (initial world)
   ↓ (player_detection Area2D triggered)
2. testing.tscn (shelburne_road) at Vector2(-3200,-2949)
   ↓ (auto-generates)
3. npc.tscn (Zea) at Vector2(-297,-1287)
   ↓ (shelburne_generate signal)
4. shelburne.tscn (town) at Vector2(-10388,-1849)
   ↓ (quest_finished signal)
5. zea_walk_cutscene.tscn (quest cutscene) at Vector2(-297,-1287)
   ↓ (cutscene_over signal)
6. scenetwo.tscn (second Zea cutscene) at Vector2(-5091.517, -3156.3)
   ↓ (cutscene_finished signal)
7. michael_plot.tscn (building area) at Vector2(-2845,-2985)
```

**Scene Signals**:
```python
# From spawn_node
"scene_triggered"        # Player entered detection area

# From shelburne_road (testing.tscn)
"shelburne_generate"     # Triggers town loading

# From shelburne.tscn
"mt_crag_over"           # Mountain cutscene finished

# From Zea NPC
"quest_is_finished"      # Quest completed

# From zea_walk_cutscene
"cutscene_over"          # First cutscene done

# From scenetwo (second Zea cutscene)
"cutscene_finished"      # Second cutscene done
```

### Camera Switching System

**Camera Deactivation** (from worldtest.gd):
```gdscript
# Cutscene camera activation
func zea_walk_cutscene():
    player.camera.enabled = false   # Disable player camera
    spawn.mysterious_cutscene.camera.enabled = false
    zea_walk_scene.quest_camera.enabled = true   # Enable cutscene camera

# Restore player camera
func deactivate_cams(variant1, variant2, variant3):
    variant1.enabled = true     # Player camera
    variant2.enabled = false    # Cutscene camera
    variant3.enabled = false    # World2 camera
```

### NPC Proximity Management (Performance Optimization)

**Distance-Based Pausing** (from worldtest.gd _process):
```gdscript
if self.has_node("npc"):
    # Check Y distance to player
    if (zea.position.y - player.position.y) > -300:
        zea.timer.paused = false   # Resume NPC roaming
    elif (zea.position.y - player.position.y) < -300:
        zea.current_state = 0      # Set to IDLE state
        zea.timer.paused = true    # Pause NPC roaming
```

### Debug Teleport Shortcuts

**Developer Shortcuts** (from worldtest.gd):
```gdscript
# Teleport to inside Zea's house
if Input.is_action_just_pressed("arrow_right"):
    player.position = Vector2(-2845,-2789)
    generate_shelburne_road()

# Teleport to Shelburne
if Input.is_action_just_pressed("Extra_key1"):
    player.position = Vector2(-4603,-1959)
    generate_shelburne()
```

### Quest Completion Teleport

**Post-Quest Movement** (from worldtest.gd):
```gdscript
func _on_npc_quest_quest_finished():
    quest_is_finished = true
    player.position = Vector2(-1000,0)   # Teleport to cutscene start
    is_pathfollowing = true
    zea_walk_cutscene()   # Trigger walking cutscene
```

### Scene Management Patterns

**Duplicate Prevention**:
```gdscript
# Check if scene already loaded before instantiating
if !self.has_node("shelburnroad"):
    # Create scene
else:
    pass   # Skip if already exists
```

**Scene References Stored**:
```python
# Global scene instance variables in worldtest.gd
spawn = None                 # spawn_node instance
shelburne_road = None        # testing.tscn instance
shelburne = None             # shelburne.tscn instance
michael_plot = None          # michael_plot.tscn instance
zea = None                   # npc.tscn instance
zea_walk_scene = None        # zea_walk_cutscene.tscn instance
zea_second_cutscene = None   # scenetwo.tscn instance
ui = None                    # ui.tscn instance
```

---

## 🌳 PROCEDURAL GENERATION (From spawn_node.gd)

**Flora Generation System**:
```gdscript
func generate_flaura():
    var gen_amount = randi_range(0, 1000)   # Random count
    for i in gen_amount:
        Tilemanager.tilemap = $spawn/TileMap2
        
        var shrub_file = preload("res://scenes/shrubs.tscn")
        var shrub_instance = shrub_file.instantiate()
        
        # Random position in range
        x_coords_candidate = randf_range(-10, 900)
        y_coords_candidate = randf_range(400, -900)
        
        # Shuffled position selection
        x_coords = choose([x_coords_candidate, x_coords_candidate, x_coords_candidate])
        y_coords = pick([y_coords_candidate, y_coords_candidate, y_coords_candidate])
        
        var random_vector = Vector2(x_coords, y_coords)
        
        # Snap to tilemap grid
        var random_tile = Tilemanager.tilemap.local_to_map(random_vector)
        var local_pos = Tilemanager.tilemap.map_to_local(random_tile)
        var world_pos = Tilemanager.tilemap.to_global(local_pos)
        
        shrub_instance.position = world_pos
        $spawn/objects.add_child(shrub_instance)

# Shuffle helpers
func choose(x_coords):
    x_coords.shuffle()
    return x_coords.front()
    
func pick(y_coords):
    y_coords.shuffle()
    return y_coords.front()
```

**Generation Bounds**:
```
X range: -10 to 900
Y range: -900 to 400
Objects: 0 to 1000 shrubs
Placement: Snapped to TileMap grid
```

---

## 📊 COORDINATE DISPLAY (From worldtest.gd)

**HUD Position Display**:
```gdscript
func _process(delta):
    # Real-time coordinate tracking
    $CanvasLayer/Label.text = str(
        int(player.global_position.x), " ", 
        int(player.global_position.y), 
        "// In scene coords: ",
        int(player.position.x * 2.75), " ",
        int(player.position.y / -2.5)
    )
```

**Coordinate Conversion**:
```
Global position → displayed directly
Scene coordinates:
  - X = player.position.x * 2.75
  - Y = player.position.y / -2.5
```

---

**Status**: Breadcrumb trail continues - extracting ONLY what's actually in the Godot files.
