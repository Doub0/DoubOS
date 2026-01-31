# Croptopia Complete Architecture Analysis
## Version: 02.11.25

---

## 1. ZONE/SCENE STRUCTURE

### Primary Zones (Top-level TSCN Files)
1. **world_2.tscn** (Main Spawn Zone)
   - Script: world_2.gd
   - Purpose: Player spawn location, opening cutscene
   - Features:
     - TileMap-based world with obstacles layer
     - Opening cutscene system (path-following camera)
     - Animation player for color fades
     - Dedicated player detection area
   - PNG Assets: `pixilart-frames/pixil-frame-0 - 2024-02-08T084127.840.png`
   - Child Scenes: cutscene path nodes, main world node

2. **shelburne.tscn** (Town Zone - Massive 37,738 lines!)
   - Script: shelburne.gd
   - Purpose: Main town/village area
   - Features:
     - TileSet with 185+ texture resources
     - 98+ child scene instances
     - Multi-layer tilemap system
   - Referenced Child Scenes:
     - roadblock.tscn
     - house_type_1.tscn, house_type_2.tscn, house_type_3.tscn
     - zea_house.tscn (NPC Zea's house)
     - wheat.tscn (crop)
     - leo_alcohol_shop.tscn
     - tall_bush_spruce.tscn
     - fence.tscn (placeable)
     - shelburne_town_mountain.tscn (entity/terrain)
     - shelburne_town_north_mountain.tscn
     - city_house.tscn
     - shelburne_bridge.tscn
     - top_of_mt_crag.tscn

3. **cave.tscn** (Underground Zone)
   - Purpose: Mining/underground exploration
   - Features: TBD (needs full read)

---

## 2. PLAYER SYSTEM

### unique_player.gd (Main Player Script)
**Key Mechanics:**
- Movement Speed: 100 (normal), 200 (sprint with SHIFT)
- Directions: up, down, left, right
- Animation States:
  - walk_{direction} (moving)
  - walk_{direction}_idle (stationary)
- Movement: 4-directional using arrow keys/WASD
- Camera: Integrated Camera2D attached to player

**Inventory System:**
- Uses Inv class (external resource)
- Collectable items:
  - stick.tres
  - pinecone
  - elderberry
  - sorrel
  - redbaneberry
  - chives

**Signals:**
- stick_collected
- pinecone_collected
- elderberry_collected
- sorrel_collected
- redbane_collected
- chive_collected

---

## 3. CROP/ITEM SYSTEM

### Collectable Items (Exists in root + scenes/)
Identified plant/item resources:
- **Trees** (harvestable):
  - oak_tree.gd + oak_tree.tscn + oak_collectable.tscn
  - birch_tree.gd + birch_tree.tscn + birch_collectable.tscn
  - maple_tree.gd + maple_tree.tscn + maple_collectable.tscn
  - elderberry_tree.gd + elderberry_tree.tscn + elderberry_collectable.tscn
  - whitepine_tree.gd + whitepine_tree.tscn (pinecone)
  - sweetgum_tree.gd + sweetgum_tree.tscn + sweetgum_collectable.tscn
  - mediumspruce_tree.gd + mediumspruce_tree.tscn
  - cranberry_bush.gd + cranberry_bush.tscn + cranberry_collectable.tscn

- **Plantable Crops**:
  - wheat.gd + wheat.tscn + wheat.tres (resource)
  - potato_crop.gd + potato_crop.tscn
  - chive.gd + chive.tscn + chive_collectable.tscn + chive_placeable.tscn
  - redbaneberry.gd + redbaneberry.tscn + redbaneberry_collectable.tscn + redbaneberry_placeable.tscn
  - sorrel.gd + sorrel.tscn + sorrel_collectable.tscn

- **Base Resources**:
  - stick.tres + stick.tscn + stick_collectable.gd
  - flint.gd + flint.tscn
  - pinecone_collectable.gd + pinecone_collectable.tscn (multiple variants)

### Resource Files (.tres)
- apricorn.tres
- catkin.tres
- chives.tres
- cranberry.tres
- elderberry.tres
- maple.tres
- smallpinecone.tres
- sorrel.tres / sorrel1.tres
- wheat.tres
- stick.tres

---

## 4. BUILDING/PLACEMENT SYSTEM

### Placeables (scenes/Placeables/)
- fence.tscn (fences)
- build_placable.gd (base placement script)

### House Types
- house_type_1.tscn
- house_type_2.tscn
- house_type_3.tscn
- zea_house.tscn (special NPC house)
- city_house.tscn

### Structures
- log_seat.gd + log_seat.tscn
- testplaceable.tscn (testing)

---

## 5. NPC & DIALOGUE SYSTEM

### NPCs Referenced
- Zea (special storyline character)
- Leo (merchant - alcohol shop)
- Philip (tool merchant - phillip_merchant.tscn)
- Mark (dialogue: mark_dialogue.tscn)
- Michael (plot: michael_plot.tscn)
- Henry (henry.tscn)
- Unknown characters (dialogue systems)

### Dialogue Files
- inside_zea_house.gd (dialogue trigger)
- dialogueplayer.gd (dialogue system)
- fourth_zea_dialogue.gd
- philip_first_dialogue.gd
- mark_dialogue.gd
- third_zea_dialogue.gd
- npc_quest.gd + npc_quest.tscn
- npc.gd + npc.tscn
- npctest.tscn

### Cutscene System
- Zea first cutscene (audio: Zea_first_cutscene.wav)
- Zea walk cutscene (zea_walk_cutscene.gd/tscn)
- News paper cutscene (newspaper.gd)
- Top of Mt. Crag cutscene (top_of_mt_crag.gd)

---

## 6. UI/HUD SYSTEM

### UI Resources
- hotbar.gd + hotbar.tscn (action bar)
- inventory.gd + inv_hotbar.tscn + inv_improved_ui.tscn
- Inv_slot.gd (inventory slot)
- pause_menu.gd + pause_menu.tscn
- game_menu.tscn (main menu)
- game_ui.tscn + game_ui_backup.tscn
- shop_ui.tscn

### UI Assets (PNG)
- hotbar_asset.png
- game_ui_panel.png
- level_frame.png
- ui_bar.png
- ui_bg.png
- seed_packet_neutral.png
- pouch.png

---

## 7. DAY/NIGHT & TIME SYSTEM

### Day/Night Cycle
- day_and_night.gd (main script)
- day_and_night.tscn
- DayNightCycle resource (.tres / .res)
- day_night_cycle_reverse.res

### Features
- Time passes/progresses
- Visual transitions
- Affects crop growth

---

## 8. AUDIO SYSTEM

### Music Files (MP3/WAV/OGG)
- pokemon_town_ahh.wav (main theme)
- Main_menu_.wav (menu music)
- Guitar_song_.m4a / Guitar_song_.mp3
- "eek! but every eek is replaced with ahh" (128 kbps)
- "Rody rich - ricch forever Instrumental"
- Zea_first_cutscene.mp3/wav
- lessee.mp3
- delete_later_aka_fnaf_music.ogg
- gunshot_ambience.mp3
- death.wav/mp3

### Audio Settings
- audio_settings.gd

---

## 9. SHADER & VISUAL EFFECTS

### Shaders
- color_depth.gdshader
- highlow.gdshader
- playboy.gdshader
- pause_menu.gdshader
- vibranto.gdshader
- shadow.gdshader (shadows)

### Animation System
- AnimatedSprite2D.gd (base sprite animation)
- AnimationLibrary resources

---

## 10. WORLD ELEMENTS

### Terrain/Obstacles
- grass_short.tscn, grass_short_mid.tscn, grass.tscn
- bush.tscn, bush_des_2.tscn, bush_v_2.tscn
- tall_bush_spruce.tscn
- shrubs.gd + shrubs.tscn (interactive bushes)

### Environmental Objects
- cave.tscn (cave entrance/interior)
- mountcrag.gd + mountcrag.tscn (mountain crags)
- stalagmite.gd + stalagmite.tscn (cave features)
- water (water tiles, water spritesheet)
- roadblock.tscn (blocking terrain)

### Terrain Assets (PNG)
- grass_2/3/4.png (different grass variants)
- dirt_9x9.png
- path_1x1.png, path_9x9.png
- road_pieces_1/2/3/4.png
- shelburne_town_road.png
- shelburne_bridge.png
- mountains_2.png, mountains_shelburne_road.png
- water_tiles_2/3.png
- corner tiles, cave tiles, intersection tiles

---

## 11. CHARACTER SPRITES & ANIMATION

### Player Animation Frames
- boycat_walkcycle.png (main player sprite)
- boy_kisser.gd + boykisser.tscn
- pixilart character frames (40+ numbered frames)
- walk animations for all 4 directions
- idle animations for all 4 directions

### NPC Sprites
- zea_spritesheet.png (Zea character)
- leo_portrait_background.png + leo_story.png + leo_walkcycle.png (Leo)
- michael_full_walk_cycle.png + michael_business_walk.png
- michael_wield_cycle.png + michael_wieldset.png + michael_death.png
- phillip_tool_shop.png (Philip/Phillip)
- federal_soldier.png + federal_helmet.png
- police_officer_sprite.png
- lunar_soldier.png
- deer_walkcycle.png (animals)
- grand-cultist-walk_forward.png (enemies)

### Enemy Sprites
- enemy_test.gd + enemy_test.tscn
- lunar_soldier.gd + lunar_soldier.tscn
- lunar_tent.gd + lunar_tent.tscn
- brock_hunt.png (hunting?)
- death.png (death state?)

---

## 12. ITEM & INVENTORY ASSETS

### Item Icons (PNG in Item Assets/)
- coal_item.png
- iron_pickaxe.png / iron_axe.png (tools)
- iron_axe_back.png / iron_axe_front.png
- raw_iron_item.png / ore_depot_*.png (ores)
- beer.png / whiskey.png / vodka.png / mead.png / jagermeister.png (drinks)
- venison_deer.png (meat)
- papers_1.png (documents)
- usd_coin.png (money)
- and many more...

---

## 13. ECONOMY/TRADING SYSTEM

### Merchant Shops
- leo_alcohol_shop.gd + leo_alcohol_shop.tscn (alcohol trading)
- phillip_merchant.gd + phillip_merchant.tscn (tools)
- house_types.gd (house building system?)

### Economy Features
- bad_economy.png / decent_economy.png / good_economy.png
- profit.png (profit tracking)
- clock_time_passed.png (time tracking)

### Resources
- economy_manager.gd (central economic logic)

---

## 14. TOOLS & CRAFTING

### Tools
- axe.gd + axe.tscn (axeslashing.png)
- crafting_menu.gd (craft interface)
- Tool shop merchant (Philip)

---

## 15. SCENE MANAGEMENT

### Loaders
- LoadManager.gd (scene transition/loading)
- loading_screen.tscn + loading_screen.png

### Scene Organization
- scenes/ folder (77+ TSCN files)
- scenes/entities/ (environmental/special entities)
- scenes/Placeables/ (placeable objects)
- scenes/formats/ (various scene formats?)

---

## 16. PROJECT STRUCTURE

### Scripts in Root (9 GD files)
- crop_node.gd
- day_and_night.tres
- leo_alcohol_shop.gd
- main.gd
- player.gd
- playerscript.gd
- tilemanager.gd

### Main Directory Structure
```
Croptopia - 02.11.25/
├── animations/         (animation frames)
├── assets/            (200+ PNG tile/sprite assets)
├── buttons/           (button UI assets)
├── dialouge/          (dialogue/story assets)
├── fonts/             (font files)
├── inventory/         (inventory UI)
├── scenes/            (93+ TSCN scene files)
│   ├── entities/      (special scene objects)
│   ├── Placeables/    (placeable items)
│   ├── formats/       (scene formatting?)
│   └── items/         (item scenes)
├── scripts/           (GD script files)
├── HTMK/              (HTML export)
├── pixilart-frames/   (sprite animation frames)
└── Item Assets/       (inventory item icons)
```

---

## 17. CRITICAL IMPORTS & DEPENDENCIES

### External Resources Referenced
- preload("res://stick.tres")
- preload("res://scenes/player.tscn")
- preload("res://scenes/entities/newspaper.tscn")
- preload("res://scenes/main.tscn")
- Signal connections via Callable()

### Asset Paths
- All PNG/texture paths use "res://" protocol (Godot internal)
- Organized by: root, assets/, scenes/, animations/

---

## 18. KNOWN FEATURES

### Implemented
- ✅ 4-directional player movement
- ✅ Animated sprites with direction-based walk/idle states
- ✅ Opening cutscene system (camera path following)
- ✅ Inventory collection system (signals)
- ✅ TileMap-based world rendering
- ✅ Multiple zones/scenes
- ✅ NPC/dialogue framework
- ✅ UI/HUD systems
- ✅ Day/night cycle
- ✅ Audio system
- ✅ Crafting menu framework

### Partially Implemented
- ⚠️ Crop/plant growth system (scripts exist, need verification)
- ⚠️ Economy/trading (merchant NPCs exist)
- ⚠️ Building placement system (exists, needs verification)
- ⚠️ Enemy AI (basic framework)

### Not Yet Confirmed
- ❓ Complete recipe system
- ❓ Full NPC quest system
- ❓ Mining/ore system details
- ❓ Fishing system
- ❓ Tool durability
- ❓ Save/load system (GameData.gd exists but minimal)

---

## 19. MAPPING REQUIREMENTS

### 1. PNG Asset Mapping (200+ files)
**Task**: Create ASSET_MAPPING.md
- Link each PNG to game element
- Track which TSCN files use each asset
- Identify duplicates/variants
- Map file: unique reference IDs in TSCN → PNG file names

### 2. Zone Transitions
**Task**: Create ZONE_TRANSITIONS.md
- world_2 ↔ shelburne (identify entry/exit points)
- shelburne → caves (identify cave entrance position)
- Town exits (roads leading to other areas)
- Interior scenes (houses, shops)

### 3. Crop/Item Database
**Task**: Create ITEMS_AND_CROPS.md
- Growth time for each crop (if stored in .tres)
- Harvest yields
- Seed requirements
- Recipes using items
- Item value/economics

### 4. NPC & Quest Log
**Task**: Create NPCS_AND_QUESTS.md
- NPC names, locations, purposes
- Dialogue options
- Quest chains
- Trading requirements
- Special events

### 5. RecipeSystem
**Task**: Extract from crafting_menu.gd and TSCN files
- What can be crafted
- Required ingredients
- Output items
- Skill requirements (if any)

---

## 20. PYTHON IMPLEMENTATION REQUIREMENTS

For DoubOS integration, the Python game engine must:

1. **Scene Management System**
   - Load/unload TSCN definitions (parse XML)
   - Manage zone transitions
   - Cache scene definitions

2. **Asset Loading**
   - Read all 200+ PNG files from correct paths
   - Build texture atlas or load individually
   - Map asset IDs to PIL Image objects

3. **Rendering Engine**
   - TileMap rendering (from parsed TSCN data)
   - Sprite animation system
   - Camera system with smooth following
   - Parallax/layering support

4. **Game Logic**
   - Player movement controller
   - Collision detection (from TileMap data)
   - Inventory system
   - Signal/event system
   - Item collection
   - NPC interaction
   - Dialogue display

5. **Time System**
   - Day/night cycle
   - Crop growth tick system
   - Time-based events

6. **Audio System**
   - Background music looping
   - Sound effects on events
   - Volume control

7. **UI System**
   - HUD rendering
   - Inventory display
   - Menu systems
   - Dialogue boxes

---

## 21. PRIORITY REBUILD CHECKLIST

### Phase 1: Core Engine
- [ ] TSCN parser (minimal - extract PNG refs, node names, positions)
- [ ] Asset loader (load all PNG files with caching)
- [ ] Scene manager (load/switch zones)
- [ ] Basic rendering (canvas drawing)

### Phase 2: Player & Movement
- [ ] Player sprite rendering
- [ ] 4-directional movement input
- [ ] Animation state machine
- [ ] Camera following

### Phase 3: World
- [ ] TileMap rendering from TSCN data
- [ ] Collision detection
- [ ] Multiple zones
- [ ] Zone transitions

### Phase 4: Items & Interaction
- [ ] Inventory system
- [ ] Collectables on ground
- [ ] Pickup system
- [ ] Item display

### Phase 5: NPCs & Dialogue
- [ ] NPC positioning
- [ ] Dialogue display
- [ ] Interaction triggers

### Phase 6: Advanced
- [ ] Day/night cycle
- [ ] Crop growth
- [ ] Crafting system
- [ ] Economy/trading

---

**Generated**: 2025-02-11
**Source**: Croptopia - 02.11.25 (497 files analyzed)
**Status**: READY FOR PYTHON IMPLEMENTATION
