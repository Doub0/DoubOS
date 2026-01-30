"""
Croptopia - Complete 2D RPG Engine
Node-based architecture mimicking Godot
Featuring Michael View's story in Shelburne
"""

import tkinter as tk
from tkinter import Canvas, Frame
from PIL import Image, ImageTk
import time
import json
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Callable, Any
from enum import Enum
import math

# ============== PATHS ==============
WORKSPACE_ROOT = Path(__file__).parent
CROPTOPIA_ASSETS = WORKSPACE_ROOT / "croptopia_assets"

# ============== SIGNAL SYSTEM ==============

class Signal:
    """Godot-style signal system for node communication"""
    def __init__(self, name: str):
        self.name = name
        self.connections: List[Callable] = []
    
    def connect(self, callback: Callable):
        """Connect a callback to this signal"""
        if callback not in self.connections:
            self.connections.append(callback)
    
    def disconnect(self, callback: Callable):
        """Disconnect a callback from this signal"""
        if callback in self.connections:
            self.connections.remove(callback)
    
    def emit(self, *args, **kwargs):
        """Emit the signal to all connected callbacks"""
        for callback in self.connections:
            callback(*args, **kwargs)

# ============== NODE SYSTEM ==============

class Node:
    """Base Node class - foundation of everything in the game"""
    def __init__(self, name: str = "Node"):
        self.name = name
        self.parent: Optional[Node] = None
        self.children: List[Node] = []
        self.signals: Dict[str, Signal] = {}
        self.position = Vector2(0, 0)
        self.visible = True
        self._process_enabled = True
        self._physics_process_enabled = False
    
    def add_child(self, child: 'Node'):
        """Add a child node"""
        child.parent = self
        self.children.append(child)
        child._ready()
    
    def remove_child(self, child: 'Node'):
        """Remove a child node"""
        if child in self.children:
            child.parent = None
            self.children.remove(child)
    
    def get_node(self, path: str) -> Optional['Node']:
        """Get a node by path"""
        if path.startswith("$"):
            path = path[1:]
        parts = path.split("/")
        current = self
        for part in parts:
            found = False
            for child in current.children:
                if child.name == part:
                    current = child
                    found = True
                    break
            if not found:
                return None
        return current
    
    def add_signal(self, signal_name: str):
        """Add a new signal to this node"""
        self.signals[signal_name] = Signal(signal_name)
    
    def emit_signal(self, signal_name: str, *args, **kwargs):
        """Emit a signal"""
        if signal_name in self.signals:
            self.signals[signal_name].emit(*args, **kwargs)
    
    def connect_signal(self, signal_name: str, callback: Callable):
        """Connect to a signal"""
        if signal_name in self.signals:
            self.signals[signal_name].connect(callback)
    
    def _ready(self):
        """Called when node enters the scene tree"""
        pass
    
    def _process(self, delta: float):
        """Called every frame"""
        if self._process_enabled:
            for child in self.children:
                child._process(delta)
    
    def _physics_process(self, delta: float):
        """Called every physics frame"""
        if self._physics_process_enabled:
            for child in self.children:
                child._physics_process(delta)

class Node2D(Node):
    """2D node with position, rotation, scale"""
    def __init__(self, name: str = "Node2D"):
        super().__init__(name)
        self.position = Vector2(0, 0)
        self.rotation = 0.0
        self.scale = Vector2(1, 1)
        self.z_index = 0

class Vector2:
    """2D Vector class"""
    def __init__(self, x: float = 0, y: float = 0):
        self.x = float(x)
        self.y = float(y)
    
    def __add__(self, other):
        return Vector2(self.x + other.x, self.y + other.y)
    
    def __sub__(self, other):
        return Vector2(self.x - other.x, self.y - other.y)
    
    def __mul__(self, scalar: float):
        return Vector2(self.x * scalar, self.y * scalar)
    
    def length(self) -> float:
        return math.sqrt(self.x ** 2 + self.y ** 2)
    
    def normalized(self):
        length = self.length()
        if length > 0:
            return Vector2(self.x / length, self.y / length)
        return Vector2(0, 0)

# ============== SPRITE SYSTEM ==============

class AnimatedSprite2D(Node2D):
    """Animated sprite node with sprite sheet support"""
    def __init__(self, name: str = "AnimatedSprite2D"):
        super().__init__(name)
        self.sprite_sheets: Dict[str, Image.Image] = {}
        self.animations: Dict[str, Dict] = {}
        self.current_animation = ""
        self.current_frame = 0
        self.frame_time = 0.0
        self.fps = 10
        self.playing = False
        self.flip_h = False
        self.cached_images: Dict[str, ImageTk.PhotoImage] = {}
    
    def load_sprite_sheet(self, name: str, path: Path, frame_width: int, frame_height: int, frames: int):
        """Load a sprite sheet"""
        try:
            img = Image.open(path)
            self.sprite_sheets[name] = img
            self.animations[name] = {
                "frame_width": frame_width,
                "frame_height": frame_height,
                "frames": frames
            }
        except Exception as e:
            print(f"Error loading sprite sheet {name}: {e}")
    
    def play(self, animation: str):
        """Play an animation"""
        if animation in self.animations:
            if self.current_animation != animation:
                self.current_animation = animation
                self.current_frame = 0
            self.playing = True
    
    def stop(self):
        """Stop animation"""
        self.playing = False
    
    def _process(self, delta: float):
        """Update animation"""
        super()._process(delta)
        if self.playing and self.current_animation:
            self.frame_time += delta
            frame_duration = 1.0 / self.fps
            if self.frame_time >= frame_duration:
                self.frame_time = 0
                anim = self.animations[self.current_animation]
                self.current_frame = (self.current_frame + 1) % anim["frames"]
    
    def get_current_sprite(self, size: tuple = (64, 64)) -> Optional[ImageTk.PhotoImage]:
        """Get the current frame as PhotoImage"""
        if not self.current_animation or self.current_animation not in self.sprite_sheets:
            return None
        
        cache_key = f"{self.current_animation}_{self.current_frame}_{size[0]}x{size[1]}_{self.flip_h}"
        if cache_key in self.cached_images:
            return self.cached_images[cache_key]
        
        try:
            sheet = self.sprite_sheets[self.current_animation]
            anim = self.animations[self.current_animation]
            
            frame_w = anim["frame_width"]
            frame_h = anim["frame_height"]
            
            x = (self.current_frame * frame_w) % sheet.width
            y = ((self.current_frame * frame_w) // sheet.width) * frame_h
            
            frame = sheet.crop((x, y, x + frame_w, y + frame_h))
            if self.flip_h:
                frame = frame.transpose(Image.FLIP_LEFT_RIGHT)
            
            frame = frame.resize(size, Image.Resampling.NEAREST)  # NEAREST for pixel art
            photo = ImageTk.PhotoImage(frame)
            self.cached_images[cache_key] = photo
            return photo
        except Exception as e:
            print(f"Error getting sprite: {e}")
            return None

# ============== PHYSICS NODES ==============

class CharacterBody2D(Node2D):
    """Character with physics and movement"""
    def __init__(self, name: str = "CharacterBody2D"):
        super().__init__(name)
        self.velocity = Vector2(0, 0)
        self.speed = 100
        self._physics_process_enabled = True
    
    def move_and_slide(self):
        """Move the character with velocity"""
        # Simple movement (no collision yet)
        pass

# ============== MICHAEL VIEW - THE PROTAGONIST ==============

class MichaelView(CharacterBody2D):
    """Michael View - the main character"""
    def __init__(self):
        super().__init__("MichaelView")
        
        # Character stats
        self.balance = 0  # Money
        self.can_move = True
        self.current_dir = "down"
        self.speed = 100  # Base speed
        
        # Inventory
        self.inventory_slots = [None] * 8
        self.selected_slot = 0
        
        # Quest items collected
        self.items_collected = {
            "pinecones": 0,
            "sticks": 0,
            "sorrel": 0,
            "redbaneberry": 0,
            "chives": 0,
            "elderberry": 0
        }
        
        # Signals
        self.add_signal("slot_1_selected")
        self.add_signal("slot_2_selected")
        self.add_signal("slot_3_selected")
        self.add_signal("slot_4_selected")
        self.add_signal("slot_5_selected")
        self.add_signal("slot_6_selected")
        self.add_signal("slot_7_selected")
        self.add_signal("slot_8_selected")
        self.add_signal("item_collected")
        
        # Animation sprite
        self.sprite = AnimatedSprite2D("Sprite")
        self.add_child(self.sprite)
        
        # Load Michael's sprite animations
        self._load_animations()
    
    def _load_animations(self):
        """Load Michael View's character sprites"""
        # boycat_walkcycle.png is the main character sprite (950x50, 19 frames of 50x50)
        sprite_path = CROPTOPIA_ASSETS / "boycat_walkcycle.png"
        if sprite_path.exists():
            self.sprite.load_sprite_sheet("walk", sprite_path, 50, 50, 19)
            self.sprite.play("walk")
    
    def _ready(self):
        """Initialize Michael"""
        super()._ready()
        self.sprite.play("walk")
    
    def _physics_process(self, delta: float):
        """Handle Michael's movement"""
        super()._physics_process(delta)
        if self.can_move:
            self.move_and_slide()
    
    def collect_item(self, item_name: str, quantity: int = 1):
        """Collect an item for Zea's quest"""
        if item_name in self.items_collected:
            self.items_collected[item_name] += quantity
            self.emit_signal("item_collected", item_name, quantity)
    
    def has_medicine_ingredients(self) -> bool:
        """Check if Michael has all ingredients for Zea's mother's medicine"""
        return (
            self.items_collected["pinecones"] >= 20 and
            self.items_collected["sticks"] >= 5 and
            self.items_collected["sorrel"] >= 5 and
            self.items_collected["redbaneberry"] >= 10 and
            self.items_collected["chives"] >= 10 and
            self.items_collected["elderberry"] >= 10
        )

# ============== QUEST SYSTEM ==============

@dataclass
class Quest:
    """Quest data structure"""
    id: str
    name: str
    description: str
    objectives: List[Dict[str, Any]]
    rewards: Dict[str, int]
    completed: bool = False
    active: bool = False

class QuestManager:
    """Manages all quests in the game"""
    def __init__(self):
        self.quests: Dict[str, Quest] = {}
        self._create_quests()
    
    def _create_quests(self):
        """Create all game quests"""
        # Zea's main quest
        self.quests["zea_medicine"] = Quest(
            id="zea_medicine",
            name="Healing Zea's Mother",
            description="Zea's mother is very sick. Gather ingredients for medicine.",
            objectives=[
                {"item": "pinecones", "required": 20, "collected": 0},
                {"item": "sticks", "required": 5, "collected": 0},
                {"item": "sorrel", "required": 5, "collected": 0},
                {"item": "redbaneberry", "required": 10, "collected": 0},
                {"item": "chives", "required": 10, "collected": 0},
                {"item": "elderberry", "required": 10, "collected": 0}
            ],
            rewards={"money": 500, "reputation": 100}
        )
    
    def get_quest(self, quest_id: str) -> Optional[Quest]:
        """Get a quest by ID"""
        return self.quests.get(quest_id)
    
    def activate_quest(self, quest_id: str):
        """Activate a quest"""
        if quest_id in self.quests:
            self.quests[quest_id].active = True
    
    def update_progress(self, quest_id: str, item: str, amount: int):
        """Update quest progress"""
        quest = self.get_quest(quest_id)
        if quest and quest.active:
            for obj in quest.objectives:
                if obj["item"] == item:
                    obj["collected"] = min(obj["collected"] + amount, obj["required"])

# ============== NPC SYSTEM ==============

class NPC(Node2D):
    """Base NPC class"""
    def __init__(self, name: str, npc_name: str, dialogue_file: str = ""):
        super().__init__(name)
        self.npc_name = npc_name
        self.dialogue_lines: List[str] = []
        self.dialogue_stage = 0
        
        if dialogue_file:
            self._load_dialogue(dialogue_file)
        
        self.add_signal("dialogue_started")
        self.add_signal("dialogue_finished")
    
    def _load_dialogue(self, filename: str):
        """Load dialogue from JSON"""
        dialogue_path = Path("C:/Users/F99500/Downloads/Croptopia - 02.11.25") / f"{filename}.json"
        try:
            if dialogue_path.exists():
                with open(dialogue_path, 'r') as f:
                    data = json.load(f)
                    self.dialogue_lines = [d["text"] for d in data]
        except Exception as e:
            print(f"Error loading dialogue for {self.npc_name}: {e}")
    
    def interact(self) -> List[str]:
        """Get current dialogue"""
        return self.dialogue_lines
    
    def advance_stage(self):
        """Move to next dialogue stage"""
        self.dialogue_stage += 1

# ============== MAIN GAME SCENE ==============

class CroptopiaGame(tk.Frame):
    """Main game - Michael View's journey in Shelburne"""
    
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        
        # Game settings
        self.TILE_SIZE = 64
        self.VIEWPORT_W = 12
        self.VIEWPORT_H = 10
        self.FPS = 60
        self.FRAME_TIME = 1000 // self.FPS
        
        # Scene tree root
        self.scene_root = Node2D("Root")
        
        # Create Michael View (protagonist)
        self.michael = MichaelView()
        self.michael.position = Vector2(6, 6)  # Starting position
        self.scene_root.add_child(self.michael)
        
        # Quest manager
        self.quest_manager = QuestManager()
        
        # Create NPCs
        self._create_npcs()
        
        # Input state
        self.keys_pressed = {}
        self.running = True
        self.last_time = time.time()
        self._sprite_refs = []
        
        # Current day
        self.day = 1
        
        # Setup UI
        self.setup_ui()
        self.bind_keys()
        
        # Start game loop
        self.after(self.FRAME_TIME, self.game_loop)
    
    def _create_npcs(self):
        """Create all NPCs in Shelburne"""
        # Zea - quest giver, Zea's daughter
        zea = NPC("Zea", "Zea", "zea_dialogue")
        zea.position = Vector2(3, 3)
        self.scene_root.add_child(zea)
        
        # Philip - merchant and quest giver
        philip = NPC("Philip", "Philip", "philip_first_dialogue")
        philip.position = Vector2(2, 5)
        self.scene_root.add_child(philip)
        
        # Leo - alcohol shop owner
        leo = NPC("Leo", "Leo")
        leo.dialogue_lines = ["Welcome to my alcohol shop!", "We have various drinks available."]
        leo.position = Vector2(9, 9)
        self.scene_root.add_child(leo)
        
        # Brock - building supplies
        brock = NPC("Brock", "Brock")
        brock.dialogue_lines = ["Hey there farmer!", "Looking for building supplies?"]
        brock.position = Vector2(10, 2)
        self.scene_root.add_child(brock)
    
    def setup_ui(self):
        """Setup game canvas and UI"""
        main_frame = Frame(self, bg="#1a1a1a")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Game canvas
        canvas_frame = Frame(main_frame, bg="#000000")
        canvas_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.canvas = Canvas(
            canvas_frame,
            width=self.VIEWPORT_W * self.TILE_SIZE,
            height=self.VIEWPORT_H * self.TILE_SIZE,
            bg="#1a3a1a",
            highlightthickness=0
        )
        self.canvas.pack()
        
        # Right panel - Character status
        right_panel = Frame(main_frame, bg="#2a2a3a", width=280)
        right_panel.pack(side=tk.RIGHT, fill=tk.Y, padx=5, pady=5)
        right_panel.pack_propagate(False)
        
        # Title
        tk.Label(right_panel, text="🌾 CROPTOPIA", bg="#2a2a3a", fg="#00ff88", 
                font=("Consolas", 16, "bold")).pack(pady=10)
        
        tk.Label(right_panel, text="Michael View's Journey", bg="#2a2a3a", fg="#88ffaa", 
                font=("Consolas", 10, "italic")).pack()
        
        # Character stats
        tk.Label(right_panel, text="\n👤 CHARACTER", bg="#2a2a3a", fg="#ffaa00", 
                font=("Consolas", 11, "bold")).pack()
        
        self.day_label = tk.Label(right_panel, text="Day: 1", bg="#2a2a3a", fg="#ffff88", 
                                 font=("Consolas", 10))
        self.day_label.pack()
        
        self.money_label = tk.Label(right_panel, text="Money: $0", bg="#2a2a3a", fg="#88ff88", 
                                    font=("Consolas", 10))
        self.money_label.pack()
        
        self.pos_label = tk.Label(right_panel, text="Position: (6, 6)", bg="#2a2a3a", fg="#8888ff", 
                                 font=("Consolas", 9))
        self.pos_label.pack()
        
        # Quest progress
        tk.Label(right_panel, text="\n📜 ACTIVE QUEST", bg="#2a2a3a", fg="#ffaa00", 
                font=("Consolas", 11, "bold")).pack()
        
        self.quest_label = tk.Label(right_panel, 
                                    text="Help Zea cure her mother\nGather medicine ingredients", 
                                    bg="#2a2a3a", fg="#aaaaaa", font=("Consolas", 8), 
                                    justify=tk.LEFT)
        self.quest_label.pack(padx=5)
        
        # Item collection progress
        tk.Label(right_panel, text="\n🎒 QUEST ITEMS", bg="#2a2a3a", fg="#ffaa00", 
                font=("Consolas", 10, "bold")).pack()
        
        self.items_frame = Frame(right_panel, bg="#2a2a3a")
        self.items_frame.pack(fill=tk.X, padx=10)
        
        self.item_labels = {}
        for item in ["pinecones", "sticks", "sorrel", "redbaneberry", "chives", "elderberry"]:
            lbl = tk.Label(self.items_frame, text=f"{item}: 0", bg="#1a1a2a", fg="#aaaaaa", 
                          font=("Consolas", 8), anchor=tk.W)
            lbl.pack(fill=tk.X, pady=1)
            self.item_labels[item] = lbl
        
        # Controls
        tk.Label(right_panel, text="\n⌨️  CONTROLS", bg="#2a2a3a", fg="#ffaa00", 
                font=("Consolas", 10, "bold")).pack()
        
        controls = """WASD/Arrows: Move
Shift+WASD: Sprint
E: Interact with NPCs
Space: Collect items
1-8: Hotbar slots
ESC: Menu"""
        
        tk.Label(right_panel, text=controls, bg="#2a2a3a", fg="#888888", 
                font=("Consolas", 8), justify=tk.LEFT).pack(padx=10, pady=5)
        
        # Dialogue box
        tk.Label(right_panel, text="\n💬 DIALOGUE", bg="#2a2a3a", fg="#ffaa00", 
                font=("Consolas", 10, "bold")).pack()
        
        dialogue_frame = Frame(right_panel, bg="#1a1a2a", relief=tk.SUNKEN, bd=2)
        dialogue_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.dialogue_text = tk.Text(dialogue_frame, height=8, width=32, 
                                     bg="#0a0a1a", fg="#88ff88", font=("Consolas", 8),
                                     wrap=tk.WORD, relief=tk.FLAT)
        self.dialogue_text.pack(fill=tk.BOTH, expand=True, padx=3, pady=3)
        self.dialogue_text.insert("1.0", "Welcome to Shelburne, Michael View.\nPress E near NPCs to talk.")
        self.dialogue_text.config(state=tk.DISABLED)
    
    def bind_keys(self):
        """Bind keyboard controls"""
        self.bind("<KeyPress>", self.on_key_down)
        self.bind("<KeyRelease>", self.on_key_up)
        self.focus_set()
    
    def on_key_down(self, event):
        """Handle key press"""
        key = event.keysym.lower()
        self.keys_pressed[key] = True
        
        # Hotbar selection
        if event.char.isdigit():
            slot = int(event.char) - 1
            if 0 <= slot < 8:
                self.michael.selected_slot = slot
                self.michael.emit_signal(f"slot_{slot+1}_selected")
        
        # Interact with NPCs
        if key == "e":
            self.interact_with_npc()
        
        # Collect items (simplified for demo)
        if key == "space":
            self.collect_nearby_item()
    
    def on_key_up(self, event):
        """Handle key release"""
        key = event.keysym.lower()
        self.keys_pressed[key] = False
    
    def interact_with_npc(self):
        """Interact with nearby NPC"""
        mx, my = int(self.michael.position.x), int(self.michael.position.y)
        
        for child in self.scene_root.children:
            if isinstance(child, NPC):
                nx, ny = int(child.position.x), int(child.position.y)
                if abs(nx - mx) <= 1 and abs(ny - my) <= 1:
                    self.show_dialogue(child)
                    
                    # Activate Zea's quest on first interaction
                    if child.npc_name == "Zea" and not self.quest_manager.get_quest("zea_medicine").active:
                        self.quest_manager.activate_quest("zea_medicine")
                    break
    
    def show_dialogue(self, npc: NPC):
        """Show NPC dialogue"""
        self.dialogue_text.config(state=tk.NORMAL)
        self.dialogue_text.delete("1.0", tk.END)
        
        dialogue = f"💬 {npc.npc_name}:\n\n"
        for i, line in enumerate(npc.dialogue_lines[:4]):
            dialogue += f"{line}\n\n"
        
        self.dialogue_text.insert("1.0", dialogue)
        self.dialogue_text.config(state=tk.DISABLED)
    
    def collect_nearby_item(self):
        """Collect items for quests (simplified)"""
        # Random collection for demo
        import random
        items = list(self.michael.items_collected.keys())
        item = random.choice(items)
        amount = random.randint(1, 3)
        
        self.michael.collect_item(item, amount)
        self.quest_manager.update_progress("zea_medicine", item, amount)
        
        # Update UI
        required = {"pinecones": 20, "sticks": 5, "sorrel": 5, "redbaneberry": 10, "chives": 10, "elderberry": 10}
        self.item_labels[item].config(
            text=f"{item}: {self.michael.items_collected[item]}/{required[item]}"
        )
    
    def update_michael_movement(self):
        """Update Michael View's movement"""
        delta = time.time() - self.last_time
        self.last_time = time.time()
        
        if not self.michael.can_move:
            return
        
        dx, dy = 0, 0
        speed = self.michael.speed
        
        # Sprint modifier
        if self.keys_pressed.get("shift_l", False) or self.keys_pressed.get("shift_r", False):
            speed = 200
        
        # 8-directional movement
        if self.keys_pressed.get("w", False) or self.keys_pressed.get("up", False):
            dy -= speed * delta
            self.michael.current_dir = "up"
        if self.keys_pressed.get("s", False) or self.keys_pressed.get("down", False):
            dy += speed * delta
            self.michael.current_dir = "down"
        if self.keys_pressed.get("a", False) or self.keys_pressed.get("left", False):
            dx -= speed * delta
            self.michael.current_dir = "left"
        if self.keys_pressed.get("d", False) or self.keys_pressed.get("right", False):
            dx += speed * delta
            self.michael.current_dir = "right"
        
        # Update position (in tiles)
        self.michael.position.x += dx / self.TILE_SIZE
        self.michael.position.y += dy / self.TILE_SIZE
        
        # Clamp to world (12x12)
        self.michael.position.x = max(0, min(11, self.michael.position.x))
        self.michael.position.y = max(0, min(11, self.michael.position.y))
        
        # Update sprite flip
        if dx < 0:
            self.michael.sprite.flip_h = True
        elif dx > 0:
            self.michael.sprite.flip_h = False
    
    def game_loop(self):
        """Main game loop"""
        if self.running:
            delta = 1.0 / self.FPS
            
            # Update
            self.update_michael_movement()
            self.scene_root._process(delta)
            self.scene_root._physics_process(delta)
            
            # Render
            self.render()
            self.update_ui()
            
            # Schedule next frame
            self.after(self.FRAME_TIME, self.game_loop)
    
    def render(self):
        """Render the game world"""
        self.canvas.delete("all")
        self._sprite_refs = []
        
        # Calculate viewport centered on Michael
        vp_x = self.michael.position.x - self.VIEWPORT_W / 2
        vp_y = self.michael.position.y - self.VIEWPORT_H / 2
        
        # Draw grass tiles (pixel art style)
        for sy in range(self.VIEWPORT_H):
            for sx in range(self.VIEWPORT_W):
                x1 = sx * self.TILE_SIZE
                y1 = sy * self.TILE_SIZE
                
                # Checkerboard grass pattern
                color = "#2a5a2a" if (sx + sy) % 2 == 0 else "#258525"
                self.canvas.create_rectangle(x1, y1, x1 + self.TILE_SIZE, y1 + self.TILE_SIZE,
                                            fill=color, outline="#1a4a1a", width=1)
        
        # Draw NPCs
        for child in self.scene_root.children:
            if isinstance(child, NPC):
                screen_x = (child.position.x - vp_x) * self.TILE_SIZE + self.TILE_SIZE // 2
                screen_y = (child.position.y - vp_y) * self.TILE_SIZE + self.TILE_SIZE // 2
                
                if 0 <= screen_x <= self.VIEWPORT_W * self.TILE_SIZE and 0 <= screen_y <= self.VIEWPORT_H * self.TILE_SIZE:
                    # NPC circle
                    self.canvas.create_oval(
                        screen_x - 24, screen_y - 28, screen_x + 24, screen_y + 28,
                        fill="#ff6b6b", outline="#aa0000", width=3
                    )
                    # Name label
                    self.canvas.create_text(screen_x, screen_y - 42, text=child.npc_name, 
                                          font=("Consolas", 9, "bold"), fill="#ffffff")
                    # Character icon
                    self.canvas.create_text(screen_x, screen_y, text="👤", font=("Arial", 24))
        
        # Draw Michael View (protagonist)
        screen_x = (self.michael.position.x - vp_x) * self.TILE_SIZE + self.TILE_SIZE // 2
        screen_y = (self.michael.position.y - vp_y) * self.TILE_SIZE + self.TILE_SIZE // 2
        
        # Get Michael's sprite
        sprite = self.michael.sprite.get_current_sprite((self.TILE_SIZE, self.TILE_SIZE))
        if sprite:
            self.canvas.create_image(int(screen_x), int(screen_y), image=sprite)
            self._sprite_refs.append(sprite)
        else:
            # Fallback character
            self.canvas.create_oval(
                screen_x - 24, screen_y - 30, screen_x + 24, screen_y + 30,
                fill="#4488ff", outline="#0044aa", width=3
            )
            self.canvas.create_text(screen_x, screen_y, text="🚶", font=("Arial", 32))
        
        # Name label
        self.canvas.create_text(screen_x, screen_y - 45, text="Michael View", 
                              font=("Consolas", 9, "bold"), fill="#ffffff", 
                              anchor=tk.CENTER)
    
    def update_ui(self):
        """Update UI labels"""
        self.day_label.config(text=f"Day: {self.day}")
        self.money_label.config(text=f"Money: ${self.michael.balance}")
        self.pos_label.config(text=f"Position: ({int(self.michael.position.x)}, {int(self.michael.position.y)})")

# ============== WINDOW INTEGRATION ==============

if __name__ == "__main__":
    root = tk.Tk()
    root.title("🌾 Croptopia - Michael View's Story")
    game = CroptopiaGame(root)
    game.pack(fill=tk.BOTH, expand=True)
    root.geometry("1400x700")
    root.mainloop()
