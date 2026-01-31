# Implementation Roadmap: Godot → Python/Pygame Translation

## Summary of Deep Dive Findings

### Architecture Overview
- **11 Main Scenes** via preload() in worldtest.gd
- **220 Asset Resources** in spawn_node alone  
- **6-Layer TileMap** system (grass, decorations, paths, structures, water, empty)
- **Frame-Based Dialogue** system (up to 8 frames per encounter)
- **Signal-Based Communication** between all systems
- **4-Phase Day/Night Cycle** with animation transitions
- **8-Slot Inventory** with item stacking and selection

### Key Pattern: Godot Signal → Python Observer
```
Godot:  obj.emit_signal("name"); other.connect("name", Callable(...))
Python: obj.emit("name"); obj.on("name", callback)  OR  event_bus.subscribe()
```

---

## TIER 1: Foundation Systems

### 1.1 Scene Manager (replaces worldtest.gd)

**File:** `croptopia_scene_manager.py`

```python
class CroptopiaSceneManager:
    """Orchestrates all subscene loading and signal routing"""
    
    def __init__(self, engine):
        self.engine = engine
        self.scenes = {}
        self.signals = {}  # Signal routing table
        self.active_scene = None
        
        # Preload all 11 scenes (Godot's preload equivalent)
        self.preload_scenes()
        self.setup_signal_connections()
    
    def preload_scenes(self):
        """Load all subscenes from preload list"""
        scenes_to_load = {
            'redbaneberry': 'Redbaneberry',
            'chive': 'Chive',
            'spawn_node': 'SpawnWorldScene',
            'ui': 'UILayer',
            'phillip_merchant': 'PhillipMerchant',
            'shelburne_road': 'ShelburneRoadScene',
            'zea_walk_cutscene': 'ZeaWalkCutscene',
            'npc': 'ZeaNPC',
            'scenetwo': 'SecondCutscene',
            'shelburne': 'ShelburneScene',
            'michael_plot': 'MichaelPlotScene'
        }
        
        for key, scene_class in scenes_to_load.items():
            self.scenes[key] = self._create_scene(scene_class)
    
    def setup_signal_connections(self):
        """Connect all signals between scenes (replaces @connection nodes)"""
        
        # spawn_node → worldtest: "scene_triggered"
        self.scenes['spawn_node'].on_signal('scene_triggered', 
                                           self.generate_shelburne_road)
        
        # world_2 → spawn_node: "cutscene_over"  
        self.scenes['world_2'].on_signal('cutscene_over',
                                        self.scenes['spawn_node'].on_cutscene_over)
        
        # michael_plot → worldtest: "cutscene_end"
        self.scenes['michael_plot'].on_signal('cutscene_end',
                                             self.on_michael_plot_end)
        
        # npc (Zea) → worldtest: "quest_is_finished"
        self.scenes['npc'].on_signal('quest_is_finished',
                                    self.on_zea_quest_finished)
        
        # player → worldtest: "redbane_selected"
        self.active_scene.player.on_signal('redbane_selected',
                                          self.on_player_redbane_selected)
    
    def generate_shelburne_road(self):
        """Called when spawn_node emits 'scene_triggered'"""
        print("Generating Shelburne Road scene...")
        self.switch_scene('shelburne_road')
    
    def on_michael_plot_end(self):
        """Called when Michael Plot cutscene finishes"""
        print("Michael Plot scene ended")
        self.switch_scene('shelburne')
    
    def on_zea_quest_finished(self):
        """Called when NPC quest completes"""
        print("Quest finished!")
        # Update game state
    
    def switch_scene(self, scene_name):
        """Unload current scene, load new one"""
        if self.active_scene:
            self.active_scene.cleanup()
        
        self.active_scene = self.scenes[scene_name]
        self.active_scene.enter()
    
    def update(self, delta):
        """Call update on active scene"""
        if self.active_scene:
            self.active_scene.update(delta)
    
    def render(self):
        """Call render on active scene"""
        if self.active_scene:
            self.active_scene.render(self.engine.display)
```

**Signal Base Class:**
```python
class SignalEmitter:
    """Replaces Godot signal system"""
    
    def __init__(self):
        self._signal_handlers = {}  # {"signal_name": [callback1, callback2, ...]}
    
    def on_signal(self, signal_name, callback):
        """Connect a callback to signal (replaces connect)"""
        if signal_name not in self._signal_handlers:
            self._signal_handlers[signal_name] = []
        self._signal_handlers[signal_name].append(callback)
    
    def emit_signal(self, signal_name, *args, **kwargs):
        """Fire signal to all connected handlers (replaces emit_signal)"""
        if signal_name in self._signal_handlers:
            for callback in self._signal_handlers[signal_name]:
                callback(*args, **kwargs)
```

---

### 1.2 Player System

**File:** `croptopia_player.py`

```python
class Player(SignalEmitter):
    """8-direction movement, animations, inventory, camera"""
    
    SPEED_WALK = 100
    SPEED_SPRINT = 200
    
    def __init__(self, position, assets):
        super().__init__()
        self.position = pygame.math.Vector2(position)
        self.velocity = pygame.math.Vector2(0, 0)
        self.assets = assets  # Preloaded sprite sheets
        
        # Animation state
        self.direction = 'down'  # down, up, left, right, down-left, etc.
        self.is_moving = False
        self.is_sprinting = False
        self.animation_frame = 0
        self.animation_timer = 0
        
        # Item system
        self.selected_item = None
        self.item_type = None
        self.item_position = pygame.math.Vector2(0, 0)
        
        # Camera
        self.camera_enabled = True
        self.camera_offset = pygame.math.Vector2(0, 0)
        
        # Signals
        self.signals_emitted = [
            'stick_collected',
            'redbane_selected',
            'chive_selected',
            'sorrel_collected',
            'chive_collected',
            'elderberry_collected',
            'pinecone_collected',
            'item_holding'
        ]
    
    def handle_input(self, keys, mouse_buttons):
        """Process keyboard and mouse input"""
        
        # 8-direction movement
        self.velocity.x = 0
        self.velocity.y = 0
        
        if keys[pygame.K_w]:
            self.velocity.y = -self.SPEED_WALK
            self.direction = 'up'
        elif keys[pygame.K_s]:
            self.velocity.y = self.SPEED_WALK
            self.direction = 'down'
        
        if keys[pygame.K_a]:
            self.velocity.x = -self.SPEED_WALK
            self.direction = 'left'
        elif keys[pygame.K_d]:
            self.velocity.x = self.SPEED_WALK
            self.direction = 'right'
        
        # Diagonal handling
        if self.velocity.x != 0 and self.velocity.y != 0:
            self.velocity *= 0.7071  # Normalize diagonal movement
            self.direction = self._get_diagonal_direction()
        
        # Sprint
        if keys[pygame.K_LSHIFT]:
            self.velocity *= (self.SPEED_SPRINT / self.SPEED_WALK)
            self.is_sprinting = True
        else:
            self.is_sprinting = False
        
        self.is_moving = self.velocity.length() > 0
    
    def update(self, delta):
        """Update position, animation, camera"""
        
        # Movement
        self.position += self.velocity * delta
        
        # Animation updates
        if self.is_moving:
            self.animation_timer += delta
            if self.animation_timer > 0.1:  # Frame duration
                self.animation_frame = (self.animation_frame + 1) % 4
                self.animation_timer = 0
        else:
            self.animation_frame = 0  # Idle pose
        
        # Camera follows player
        if self.camera_enabled:
            self.camera_offset = self.position  # Center on player
    
    def on_item_collected(self, item_name):
        """Emit signal when item collected"""
        signal = f"{item_name}_collected"
        self.emit_signal(signal)
        self.selected_item = item_name
    
    def on_item_selected(self, item_type):
        """User selected item from inventory"""
        self.item_type = item_type
        self.emit_signal('item_holding', item_type)
    
    def render(self, display, camera_pos):
        """Draw player sprite, items, effects"""
        
        # Calculate screen position relative to camera
        screen_pos = self.position - camera_pos
        
        # Draw player sprite based on direction and animation frame
        sprite_key = f"player_{self.direction}_{'walk' if self.is_moving else 'idle'}"
        if sprite_key in self.assets:
            frame = self.assets[sprite_key][self.animation_frame]
            display.blit(frame, screen_pos)
        
        # Draw item if holding
        if self.item_type:
            item_sprite = self._get_item_sprite(self.item_type, self.direction)
            item_offset = self._get_item_offset(self.direction)
            display.blit(item_sprite, screen_pos + item_offset)
    
    def _get_diagonal_direction(self):
        """Map diagonal velocity to cardinal + diagonal strings"""
        if self.velocity.x < 0:  # Left
            if self.velocity.y < 0:
                return 'up-left'
            else:
                return 'down-left'
        else:  # Right
            if self.velocity.y < 0:
                return 'up-right'
            else:
                return 'down-right'
    
    def _get_item_sprite(self, item_type, direction):
        """Get sprite for currently held item"""
        # Map: axe → iron_axe.png, redbaneberry → redbane_sprite.png, etc.
        return self.assets.get(f"{item_type}_{direction}", 
                               self.assets.get(f"{item_type}_default"))
    
    def _get_item_offset(self, direction):
        """Offset item sprite based on player direction"""
        offsets = {
            'up': (8, -16),
            'down': (8, 16),
            'left': (-16, 0),
            'right': (16, 0),
            # etc for diagonals
        }
        return pygame.math.Vector2(offsets.get(direction, (0, 0)))
```

---

### 1.3 TileMap Renderer

**File:** `croptopia_tilemap.py`

```python
class TileMapRenderer:
    """Parse and render multi-layer TileMap data"""
    
    TILE_SIZE = 16  # Base size (scaled to 32 in engine)
    LAYER_COUNT = 6
    
    def __init__(self, assets):
        self.assets = assets  # Preloaded tile sprites
        self.layers = [[] for _ in range(self.LAYER_COUNT)]
        self.tile_map_data = {}  # Dict of layer → tiles
        self.spawn_world_bounds = None
    
    def load_tilemap_from_tscn(self, tscn_file):
        """Parse .tscn file and extract tile_data"""
        
        with open(tscn_file, 'r') as f:
            content = f.read()
        
        # Extract all layer_X/tile_data entries
        import re
        
        layer_pattern = r'layer_(\d+)/name = "([^"]+)".*?layer_\d+/tile_data = PackedInt32Array\(([^\)]+)\)'
        
        for match in re.finditer(layer_pattern, content, re.DOTALL):
            layer_idx = int(match.group(1))
            layer_name = match.group(2)
            tile_data_str = match.group(3)
            
            tiles = self._parse_tile_data(tile_data_str)
            self.tile_map_data[layer_idx] = {
                'name': layer_name,
                'tiles': tiles
            }
    
    def _parse_tile_data(self, tile_data_str):
        """Parse PackedInt32Array format into tile dicts"""
        
        # Format: x, y (packed), source_id, atlas_coords
        # Example: 0, 2, 0 → tile at (0,0) from source 2, atlas coord 0
        
        tile_ints = [int(x.strip()) for x in tile_data_str.split(',') if x.strip()]
        tiles = []
        
        i = 0
        while i < len(tile_ints):
            packed_pos = tile_ints[i]
            source_id = tile_ints[i+1] if i+1 < len(tile_ints) else 0
            atlas_coord = tile_ints[i+2] if i+2 < len(tile_ints) else 0
            
            # Decode packed position (bit-packed x, y coordinates)
            x = packed_pos & 0xFFFF
            y = (packed_pos >> 16) & 0xFFFF
            
            # Handle negative coordinates (2's complement)
            if x > 32767:
                x = -(65536 - x)
            if y > 32767:
                y = -(65536 - y)
            
            tiles.append({
                'position': (x, y),
                'source_id': source_id,
                'atlas_coord': atlas_coord
            })
            
            i += 3
        
        return tiles
    
    def render_layers(self, display, camera_pos, viewport_size):
        """Render all layers in order with proper Z-ordering"""
        
        camera_rect = pygame.Rect(camera_pos.x, camera_pos.y, 
                                  viewport_size[0], viewport_size[1])
        
        for layer_idx in range(self.LAYER_COUNT):
            if layer_idx not in self.tile_map_data:
                continue
            
            layer_info = self.tile_map_data[layer_idx]
            tiles = layer_info['tiles']
            
            # Render each tile in layer
            for tile in tiles:
                screen_x = tile['position'][0] * self.TILE_SIZE - camera_pos.x
                screen_y = tile['position'][1] * self.TILE_SIZE - camera_pos.y
                
                # Cull tiles outside viewport
                if not (-64 < screen_x < viewport_size[0] + 64 and
                        -64 < screen_y < viewport_size[1] + 64):
                    continue
                
                # Get sprite for this tile
                source_id = tile['source_id']
                sprite = self._get_tile_sprite(source_id, tile['atlas_coord'])
                
                if sprite:
                    display.blit(sprite, (screen_x, screen_y))
    
    def _get_tile_sprite(self, source_id, atlas_coord):
        """Look up tile sprite from asset library"""
        
        # Map source_id → texture asset
        # Map atlas_coord → position in spritesheet
        
        key = f"tileset_{source_id}_{atlas_coord}"
        return self.assets.get(key)
```

---

### 1.4 UI Canvas System

**File:** `croptopia_ui.py`

```python
class UICanvas(SignalEmitter):
    """Canvas layer system replacing Godot's CanvasLayer"""
    
    def __init__(self, engine):
        super().__init__()
        self.engine = engine
        self.layers = {}  # layer_id → UILayer
        self.visible_layers = set()
        
        # Create UI layers
        self._create_layers()
    
    def _create_layers(self):
        """Create all UI layers from ui.tscn"""
        
        # Layer 0: Game world (rendered by scene)
        # Layer 2: Inventory overlay
        self.layers[2] = UILayer(2)
        self.layers[2].add_component('inventory', InventoryUI())
        self.layers[2].add_component('crafting', CraftingMenuUI())
        
        # Layer 3: Pause/overlays
        self.layers[3] = UILayer(3)
        self.layers[3].add_component('pause_menu', PauseMenuUI())
        self.layers[3].add_component('death_screen', DeathScreenUI())
        
        # Layer 4: HUD
        self.layers[4] = UILayer(4)
        self.layers[4].add_component('hotbar', HotbarUI())
        self.layers[4].add_component('day_night', DayNightUI())
        self.layers[4].add_component('money_counter', MoneyCounterUI())
        self.layers[4].add_component('stat_bars', StatBarsUI())
    
    def update(self, delta):
        """Update all visible UI layers"""
        for layer_id in self.visible_layers:
            if layer_id in self.layers:
                self.layers[layer_id].update(delta)
    
    def render(self, display):
        """Render all visible UI layers in order"""
        for layer_id in sorted(self.visible_layers):
            if layer_id in self.layers:
                self.layers[layer_id].render(display)
    
    def show_layer(self, layer_id):
        """Make layer visible"""
        self.visible_layers.add(layer_id)
    
    def hide_layer(self, layer_id):
        """Hide layer"""
        self.visible_layers.discard(layer_id)

class UILayer:
    """Single UI layer containing components"""
    
    def __init__(self, layer_id):
        self.layer_id = layer_id
        self.components = {}  # component_name → UIComponent
    
    def add_component(self, name, component):
        """Add UI element to this layer"""
        self.components[name] = component
    
    def update(self, delta):
        """Update all components in layer"""
        for component in self.components.values():
            component.update(delta)
    
    def render(self, display):
        """Draw all components in layer"""
        for component in self.components.values():
            component.render(display)

class HotbarUI:
    """3x3 item slot grid at (239, 544)"""
    
    def __init__(self):
        self.position = pygame.math.Vector2(239, 544)
        self.slot_size = 32
        self.slots = [None] * 9  # 3x3 grid
        self.selected_slot = 0
    
    def on_item_selected(self, slot_idx, item):
        """Update slot with item"""
        self.slots[slot_idx] = item
    
    def render(self, display):
        """Draw 3x3 grid"""
        for i in range(9):
            row = i // 3
            col = i % 3
            
            x = self.position.x + col * self.slot_size
            y = self.position.y + row * self.slot_size
            
            # Draw slot background
            pygame.draw.rect(display, (100, 100, 100), 
                           (x, y, self.slot_size, self.slot_size))
            
            # Draw item if present
            if self.slots[i]:
                # Display item sprite
                pass
            
            # Draw selection highlight if selected
            if i == self.selected_slot:
                pygame.draw.rect(display, (255, 255, 0), 
                               (x, y, self.slot_size, self.slot_size), 2)

class DayNightUI:
    """Time display showing day, month, year, time"""
    
    def __init__(self):
        self.day_count = 1
        self.month = "JAN"
        self.year = 2027
        self.hour = "00"
        self.minute = "00"
        self.phase = "day"  # day, sunset, night, sunrise
        
        self.position = pygame.math.Vector2(10, 10)
        self.font = pygame.font.Font(None, 24)
    
    def set_time(self, day, month, year, hour, minute):
        """Update time display"""
        self.day_count = day
        self.month = month
        self.year = year
        self.hour = f"{hour:02d}"
        self.minute = f"{minute:02d}"
    
    def render(self, display):
        """Draw time information"""
        time_text = f"{self.hour}:{self.minute}"
        date_text = f"{self.month} {self.day_count}, {self.year}"
        
        time_surf = self.font.render(time_text, True, (255, 255, 255))
        date_surf = self.font.render(date_text, True, (255, 255, 255))
        
        display.blit(time_surf, self.position)
        display.blit(date_surf, (self.position.x, self.position.y + 25))
```

---

## Connection Strategy

Each Tier 1 system needs to be integrated:

```python
class CroptopiaEngine:
    def __init__(self):
        self.assets = AssetManager()  # Load all 200+ assets
        self.player = Player((12, -11), self.assets)
        self.tilemap = TileMapRenderer(self.assets)
        self.ui = UICanvas(self)
        self.scene_manager = CroptopiaSceneManager(self)
        
        # Wire up all signals
        self.player.on_signal('redbane_selected', 
                             self.on_player_redbane_selected)
        self.scene_manager.scenes['spawn_node'].on_signal(
            'scene_triggered', self.on_spawn_scene_triggered)
    
    def update(self, delta):
        self.player.handle_input(pygame.key.get_pressed(), pygame.mouse.get_pressed())
        self.player.update(delta)
        self.tilemap.update(delta)  # If animated tiles
        self.ui.update(delta)
        self.scene_manager.update(delta)
    
    def render(self):
        # Render order: TileMap (0), World objects, Player, UI (layered)
        self.tilemap.render_layers(self.display, self.player.camera_offset, 
                                   self.VIEWPORT_SIZE)
        self.player.render(self.display, self.player.camera_offset)
        self.ui.render(self.display)
```

---

## Summary: TIER 1 Deliverables

✅ Scene Manager orchestration (preload + signal routing)
✅ Player with 8-direction movement + animations
✅ TileMap multi-layer renderer with asset mapping
✅ UI Canvas system with hotbar, HUD, overlays

**Estimated lines of code:** ~2,500-3,000 lines for full Tier 1

All other tiers (Tier 2-4) build on these foundations.

