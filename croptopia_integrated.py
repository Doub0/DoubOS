"""
Croptopia - Fully Integrated with Local Assets & Dialogue
Complete Python recreation of Godot Croptopia game
Uses local croptopia_assets folder for all game data
"""

import tkinter as tk
from tkinter import Canvas, Frame, Label, Button, Text
from PIL import Image, ImageTk
import os
import json
import random
import time
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional
from enum import Enum

# ============== PATHS ==============
# Get the workspace root
WORKSPACE_ROOT = Path(__file__).parent
CROPTOPIA_ASSETS = WORKSPACE_ROOT / "croptopia_assets"
DIALOGUE_PATH = CROPTOPIA_ASSETS

# ============== DATA CLASSES ==============

class ItemType(Enum):
    CROP = "crop"
    COLLECTABLE = "collectable"
    TREE = "tree"
    TOOL = "tool"
    BUILDING = "building"

@dataclass
class Item:
    name: str
    item_type: ItemType
    image_name: str = ""
    stackable: bool = True
    quantity: int = 1

@dataclass
class InvSlot:
    item: Optional[Item] = None
    amount: int = 0

@dataclass
class CropData:
    crop_type: str
    growth_stage: int  # 0=seed, 1=sprout, 2=grown, 3=harvestable
    x: int
    y: int
    plant_time: float = 0.0
    
@dataclass
class TreeData:
    tree_type: str
    x: int
    y: int
    has_fruit: bool = True
    regrow_time: float = 0.0

@dataclass
class NPCData:
    name: str
    x: int
    y: int
    dialogue_lines: List[str] = field(default_factory=list)
    image_name: str = ""

# ============== DIALOGUE LOADER ==============

class DialogueLoader:
    """Load dialogue from actual JSON files in Croptopia"""
    
    @staticmethod
    def load_dialogue(filename: str) -> List[Dict]:
        """Load dialogue from JSON file"""
        try:
            dialogue_file = DIALOGUE_PATH / f"{filename}.json"
            if dialogue_file.exists():
                with open(dialogue_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading dialogue {filename}: {e}")
        return []
    
    @staticmethod
    def get_dialogue_lines(dialogue_list: List[Dict]) -> List[str]:
        """Extract just the text from dialogue JSON"""
        return [d.get("text", "") for d in dialogue_list if "text" in d]

# ============== SPRITE LOADER ==============

class SpriteLoader:
    """Load sprites from actual Croptopia PNG files"""
    
    def __init__(self):
        self.cache = {}
        self.sprite_sheets = {}
        self._load_sprite_sheets()
    
    def _load_sprite_sheets(self):
        """Load all sprite sheet images"""
        try:
            # Load character sprites
            if (CROPTOPIA_ASSETS / "boycat_walkcycle.png").exists():
                self.sprite_sheets["player"] = Image.open(CROPTOPIA_ASSETS / "boycat_walkcycle.png")
            
            # Load crop/plant sprites
            if (CROPTOPIA_ASSETS / "potato sprites.png").exists():
                self.sprite_sheets["crops"] = Image.open(CROPTOPIA_ASSETS / "potato sprites.png")
            
            # Load tree/plant sprites
            if (CROPTOPIA_ASSETS / "whitepine.png").exists():
                self.sprite_sheets["trees"] = Image.open(CROPTOPIA_ASSETS / "whitepine.png")
            
            if (CROPTOPIA_ASSETS / "cranberry.png").exists():
                self.sprite_sheets["cranberry"] = Image.open(CROPTOPIA_ASSETS / "cranberry.png")
            
            if (CROPTOPIA_ASSETS / "redbaneberry.png").exists():
                self.sprite_sheets["redbaneberry"] = Image.open(CROPTOPIA_ASSETS / "redbaneberry.png")
            
            # Load action sprites
            if (CROPTOPIA_ASSETS / "axeslashing.png").exists():
                self.sprite_sheets["axe"] = Image.open(CROPTOPIA_ASSETS / "axeslashing.png")
            
            if (CROPTOPIA_ASSETS / "adobe_pixelart.png").exists():
                self.sprite_sheets["tileset"] = Image.open(CROPTOPIA_ASSETS / "adobe_pixelart.png")
            
            print(f"✓ Loaded {len(self.sprite_sheets)} sprite sheets")
        except Exception as e:
            print(f"Error loading sprite sheets: {e}")
    
    def get_sprite(self, sprite_type: str, index: int = 0, size: Tuple[int, int] = (64, 64)) -> Optional[ImageTk.PhotoImage]:
        """Get a sprite from a sprite sheet"""
        cache_key = f"{sprite_type}_{index}_{size[0]}x{size[1]}"
        
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        try:
            if sprite_type not in self.sprite_sheets:
                return None
            
            sheet = self.sprite_sheets[sprite_type]
            
            # Extract sprite based on type
            if sprite_type == "player":
                # boycat_walkcycle.png is 950x50px, appears to be 19 frames of 50x50
                frame_width = 50
                frame_height = 50
                x = (index % 19) * frame_width
                y = 0
            elif sprite_type == "crops":
                # potato sprites is 160x64px, 4 frames of 40x64
                frame_width = 40
                frame_height = 64
                x = (index % 4) * frame_width
                y = 0
            elif sprite_type in ["trees", "cranberry", "redbaneberry"]:
                # Use full image as sprite
                img = sheet
            elif sprite_type == "axe":
                # axeslashing is 200x50px, multiple frames
                frame_width = 50
                frame_height = 50
                x = (index % 4) * frame_width
                y = 0
            else:
                img = sheet
            
            # Crop the sprite if we have coordinates
            if 'img' not in locals():
                img = sheet.crop((x, y, x + frame_width, y + frame_height))
            
            # Resize to target size
            img = img.resize(size, Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            self.cache[cache_key] = photo
            return photo
        
        except Exception as e:
            print(f"Error getting sprite {sprite_type}: {e}")
            return None

# ============== ASSET MANAGER ==============

class AssetManager:
    """Manage all game assets from local Croptopia folder"""
    
    def __init__(self):
        self.sprites = SpriteLoader()
        self.available_files = self._discover_assets()
    
    def _discover_assets(self) -> Dict[str, Path]:
        """Find all PNG files in Croptopia folder"""
        assets = {}
        if CROPTOPIA_ASSETS.exists():
            for filepath in CROPTOPIA_ASSETS.glob("*.png"):
                filename = filepath.name.lower()
                assets[filename] = filepath
        return assets
    
    def load_image(self, filename: str, size: Tuple[int, int] = (64, 64)) -> Optional[ImageTk.PhotoImage]:
        """Load any PNG file by filename"""
        try:
            for asset_name, asset_path in self.available_files.items():
                if filename.lower() in asset_name:
                    img = Image.open(asset_path)
                    img = img.resize(size, Image.Resampling.LANCZOS)
                    return ImageTk.PhotoImage(img)
        except Exception as e:
            print(f"Error loading {filename}: {e}")
        return None

# ============== GAME STATE ==============

class GameState:
    """Maintain complete game state"""
    
    def __init__(self):
        # Player
        self.player_x = 6.0  # Center of 12x12 world
        self.player_y = 6.0
        self.player_direction = "down"
        
        # Economy
        self.money = 100
        self.day = 1
        
        # Inventory (8-slot hotbar)
        self.inventory: List[InvSlot] = [InvSlot() for _ in range(8)]
        self.selected_slot = 0
        
        # World (12x12)
        self.world_width = 12
        self.world_height = 12
        self.crops: Dict[Tuple[int, int], CropData] = {}
        self.trees: Dict[Tuple[int, int], TreeData] = {}
        self.buildings: Dict[Tuple[int, int], str] = {}
        
        # NPCs - Load dialogue from actual JSON files
        self.npcs: Dict[str, NPCData] = {
            "zea": NPCData(
                "Zea", 3, 3,
                dialogue_lines=DialogueLoader.get_dialogue_lines(
                    DialogueLoader.load_dialogue("zea_dialogue")
                ) or ["Hello! Nice to meet you!"]
            ),
            "philip": NPCData(
                "Philip", 2, 5,
                dialogue_lines=DialogueLoader.get_dialogue_lines(
                    DialogueLoader.load_dialogue("philip_first_dialogue")
                ) or ["Hi, I'm Philip!"]
            ),
            "leo": NPCData(
                "Leo", 9, 9,
                dialogue_lines=["Welcome to my alcohol shop!", "We have various drinks available."]
            ),
            "brock": NPCData(
                "Brock", 10, 2,
                dialogue_lines=["Hey there farmer!", "Looking for building supplies?"]
            ),
        }
        
        # Dialogue state
        self.active_dialogue = None
        self.dialogue_line = 0
    
    def save(self) -> Dict:
        """Save game state to dict"""
        return {
            "player": {"x": self.player_x, "y": self.player_y, "direction": self.player_direction},
            "economy": {"money": self.money, "day": self.day},
            "crops": {str(k): v.__dict__ for k, v in self.crops.items()},
            "trees": {str(k): v.__dict__ for k, v in self.trees.items()},
            "buildings": self.buildings,
        }

# ============== CROP SYSTEM ==============

class CropSystem:
    """Manage crops with growth stages"""
    
    CROP_TYPES = {
        "wheat": {"emoji": "🌾", "growth_time": 5.0, "harvest_reward": 10},
        "potato": {"emoji": "🥔", "growth_time": 6.0, "harvest_reward": 15},
        "chive": {"emoji": "🧅", "growth_time": 4.0, "harvest_reward": 8},
        "cranberry": {"emoji": "🫐", "growth_time": 7.0, "harvest_reward": 20},
        "sorrel": {"emoji": "🍃", "growth_time": 4.5, "harvest_reward": 5},
        "redbaneberry": {"emoji": "🫒", "growth_time": 8.0, "harvest_reward": 12},
        "elderberry": {"emoji": "🫐", "growth_time": 6.5, "harvest_reward": 10},
        "pinecone": {"emoji": "🌲", "growth_time": 10.0, "harvest_reward": 5},
        "stick": {"emoji": "🪵", "growth_time": 0.5, "harvest_reward": 1},
        "flint": {"emoji": "⚒️", "growth_time": 3.0, "harvest_reward": 3},
    }
    
    GROWTH_STAGES = ["🌱", "🌿", "🌾", "✓"]
    
    @staticmethod
    def plant_crop(state: GameState, x: int, y: int, crop_type: str):
        """Plant a crop at position"""
        if 0 <= x < state.world_width and 0 <= y < state.world_height:
            if (x, y) not in state.crops and (x, y) not in state.buildings:
                state.crops[(x, y)] = CropData(
                    crop_type=crop_type,
                    growth_stage=0,
                    x=x, y=y,
                    plant_time=time.time()
                )
                return True
        return False
    
    @staticmethod
    def update_crops(state: GameState):
        """Update crop growth"""
        current_time = time.time()
        
        for pos, crop in state.crops.items():
            if crop.growth_stage < 3:
                age = current_time - crop.plant_time
                growth_time = CropSystem.CROP_TYPES[crop.crop_type]["growth_time"]
                
                new_stage = int((age / growth_time) * 3)
                if new_stage >= 3:
                    crop.growth_stage = 3
                else:
                    crop.growth_stage = min(2, new_stage)
    
    @staticmethod
    def harvest_crop(state: GameState, x: int, y: int) -> bool:
        """Harvest a crop"""
        if (x, y) in state.crops:
            crop = state.crops[(x, y)]
            if crop.growth_stage == 3:
                reward = CropSystem.CROP_TYPES[crop.crop_type]["harvest_reward"]
                state.money += reward
                del state.crops[(x, y)]
                return True
        return False

# ============== TREE SYSTEM ==============

class TreeSystem:
    """Manage trees and collectables"""
    
    TREE_TYPES = {
        "birch": {"emoji": "🌳", "item": "birch_wood", "regrow_time": 10.0},
        "oak": {"emoji": "🌳", "item": "oak_wood", "regrow_time": 12.0},
        "maple": {"emoji": "🍁", "item": "maple_leaf", "regrow_time": 8.0},
        "pine": {"emoji": "🌲", "item": "pinecone", "regrow_time": 15.0},
        "white_pine": {"emoji": "🌲", "item": "pinecone", "regrow_time": 15.0},
        "sweet_gum": {"emoji": "🌳", "item": "sweet_gum_ball", "regrow_time": 10.0},
        "medium_spruce": {"emoji": "🌲", "item": "spruce_cone", "regrow_time": 14.0},
        "elderberry": {"emoji": "🫐", "item": "elderberry", "regrow_time": 6.0},
    }
    
    @staticmethod
    def spawn_trees(state: GameState):
        """Place initial trees around world"""
        tree_positions = [
            (1, 1), (1, 10), (10, 1), (10, 10),
            (5, 5), (6, 7), (7, 4), (3, 8), (8, 2),
        ]
        for x, y in tree_positions:
            if (x, y) not in state.trees and (x, y) not in state.buildings:
                tree_type = random.choice(list(TreeSystem.TREE_TYPES.keys()))
                state.trees[(x, y)] = TreeData(tree_type, x, y, has_fruit=True)
    
    @staticmethod
    def harvest_tree(state: GameState, x: int, y: int) -> bool:
        """Harvest a tree"""
        if (x, y) in state.trees:
            tree = state.trees[(x, y)]
            if tree.has_fruit:
                item_name = TreeSystem.TREE_TYPES[tree.tree_type]["item"]
                state.money += 5
                tree.has_fruit = False
                tree.regrow_time = time.time() + TreeSystem.TREE_TYPES[tree.tree_type]["regrow_time"]
                return True
        return False

# ============== BUILDING SYSTEM ==============

class BuildingSystem:
    """Manage placeable buildings"""
    
    BUILDING_TYPES = {
        "fence": {"emoji": "🚧", "cost": 10},
        "chest": {"emoji": "🏺", "cost": 50},
        "house": {"emoji": "🏠", "cost": 100},
    }
    
    @staticmethod
    def place_building(state: GameState, x: int, y: int, building_type: str) -> bool:
        """Place a building"""
        if building_type not in BuildingSystem.BUILDING_TYPES:
            return False
        
        cost = BuildingSystem.BUILDING_TYPES[building_type]["cost"]
        
        if (x, y) not in state.buildings and (x, y) not in state.crops:
            if state.money >= cost:
                state.money -= cost
                state.buildings[(x, y)] = building_type
                return True
        return False

# ============== MAIN GAME ==============

class CropTopiaGame(tk.Frame):
    """Main game implementation - fully integrated with local Croptopia assets"""
    
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        
        # Settings
        self.TILE_SIZE = 64
        self.VIEWPORT_W = 12
        self.VIEWPORT_H = 10
        self.FPS = 60
        self.FRAME_TIME = 1000 // self.FPS
        
        # Game state
        self.state = GameState()
        self.assets = AssetManager()
        
        # Log asset discovery
        print(f"Assets found: {len(self.assets.available_files)}")
        print(f"Sprites loaded: {len(self.assets.sprites.sprite_sheets)}")
        
        # Initial setup
        TreeSystem.spawn_trees(self.state)
        
        # UI State
        self.keys_pressed = {}
        self.running = True
        self.last_time = time.time()
        self._sprite_refs = []  # Keep sprite references to prevent garbage collection
        
        # Setup UI
        self.setup_ui()
        self.bind_keys()
        
        # Start game loop
        self.after(self.FRAME_TIME, self.game_loop)
    
    def setup_ui(self):
        """Setup game canvas and UI panels"""
        main_frame = Frame(self, bg="#2a2a2a")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Game canvas (left side)
        canvas_frame = Frame(main_frame, bg="#1a1a1a")
        canvas_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.canvas = Canvas(
            canvas_frame,
            width=self.VIEWPORT_W * self.TILE_SIZE,
            height=self.VIEWPORT_H * self.TILE_SIZE,
            bg="#000000",
            highlightthickness=0
        )
        self.canvas.pack()
        self.canvas.bind("<Button-1>", self.on_click)
        
        # Right panel
        right_panel = Frame(main_frame, bg="#3a3a3a", width=250)
        right_panel.pack(side=tk.RIGHT, fill=tk.Y, padx=5, pady=5)
        right_panel.pack_propagate(False)
        
        # Title
        Label(right_panel, text="🌾 CROPTOPIA", bg="#3a3a3a", fg="#00ff00", 
              font=("Arial", 14, "bold")).pack(pady=10)
        
        # Stats
        self.day_label = Label(right_panel, text="Day: 1", bg="#3a3a3a", fg="#ffff00", 
                              font=("Arial", 10))
        self.day_label.pack()
        
        self.money_label = Label(right_panel, text="Money: 100", bg="#3a3a3a", fg="#00ff00", 
                                font=("Arial", 10))
        self.money_label.pack()
        
        self.pos_label = Label(right_panel, text="Pos: 6, 6", bg="#3a3a3a", fg="#0088ff", 
                              font=("Arial", 10))
        self.pos_label.pack()
        
        # Inventory section
        Label(right_panel, text="\n📦 HOTBAR", bg="#3a3a3a", fg="#00ff00", 
              font=("Arial", 10, "bold")).pack()
        
        self.inv_labels = []
        for i in range(8):
            lbl = Label(right_panel, text=f"[{i+1}] Empty", bg="#2a2a2a", fg="#aaaaaa", 
                       font=("Arial", 8))
            lbl.pack(fill=tk.X, padx=5, pady=2)
            self.inv_labels.append(lbl)
        
        # Actions
        Label(right_panel, text="\n⚙️  ACTIONS", bg="#3a3a3a", fg="#00ff00", 
              font=("Arial", 10, "bold")).pack()
        
        Button(right_panel, text="Next Day", command=self.next_day, 
               bg="#0088ff", fg="#ffffff", font=("Arial", 10)).pack(fill=tk.X, padx=5, pady=5)
        
        Button(right_panel, text="Plant Wheat", command=lambda: self.quick_plant("wheat"), 
               bg="#00aa00", fg="#ffffff", font=("Arial", 9)).pack(fill=tk.X, padx=5, pady=2)
        
        Button(right_panel, text="Place Fence", command=lambda: self.quick_place("fence"), 
               bg="#ffaa00", fg="#000000", font=("Arial", 9)).pack(fill=tk.X, padx=5, pady=2)
        
        # Instructions
        Label(right_panel, text="\n📖 CONTROLS", bg="#3a3a3a", fg="#00ff00", 
              font=("Arial", 10, "bold")).pack()
        
        instructions = """Arrow Keys: Move
Click: Plant/Harvest
E: Open dialogue
Space: Next day
1-8: Hotbar slots"""
        
        Label(right_panel, text=instructions, bg="#3a3a3a", fg="#aaaaaa", 
              font=("Arial", 8), justify=tk.LEFT).pack(padx=5, pady=5)
        
        # Dialogue area
        Label(right_panel, text="\n💬 DIALOGUE", bg="#3a3a3a", fg="#00ff00", 
              font=("Arial", 10, "bold")).pack()
        
        self.dialogue_text = Text(right_panel, height=6, width=30, 
                                 bg="#1a1a1a", fg="#00ff00", font=("Arial", 8))
        self.dialogue_text.pack(padx=5, pady=5, fill=tk.BOTH, expand=True)
        
        # Asset status
        Label(right_panel, text=f"\n📁 Sprites Loaded: {len(self.assets.sprites.sprite_sheets)}", 
              bg="#3a3a3a", fg="#ffaa00", font=("Arial", 8)).pack(padx=5)
    
    def bind_keys(self):
        """Bind keyboard events"""
        self.bind("<KeyPress>", self.on_key_down)
        self.bind("<KeyRelease>", self.on_key_up)
        self.focus_set()
    
    def on_key_down(self, event):
        """Handle key press"""
        key = event.keysym.lower()
        self.keys_pressed[key] = True
        
        if event.char.isdigit():
            slot = int(event.char) - 1
            if 0 <= slot < 8:
                self.state.selected_slot = slot
        
        if key == "space":
            self.next_day()
        
        if key == "e":
            self.interact_npc()
    
    def on_key_up(self, event):
        """Handle key release"""
        key = event.keysym.lower()
        self.keys_pressed[key] = False
    
    def on_click(self, event):
        """Handle mouse click"""
        canvas_x = event.x
        canvas_y = event.y
        
        vp_x = self.state.player_x - self.VIEWPORT_W / 2
        vp_y = self.state.player_y - self.VIEWPORT_H / 2
        
        world_x = vp_x + (canvas_x / self.TILE_SIZE)
        world_y = vp_y + (canvas_y / self.TILE_SIZE)
        
        x, y = int(world_x), int(world_y)
        
        if (x, y) in self.state.crops:
            CropSystem.harvest_crop(self.state, x, y)
        else:
            CropSystem.plant_crop(self.state, x, y, "wheat")
    
    def interact_npc(self):
        """Interact with nearby NPC"""
        px, py = int(self.state.player_x), int(self.state.player_y)
        
        for name, npc in self.state.npcs.items():
            if abs(npc.x - px) <= 1 and abs(npc.y - py) <= 1:
                self.show_dialogue(npc)
                break
    
    def show_dialogue(self, npc: NPCData):
        """Show NPC dialogue"""
        self.dialogue_text.config(state=tk.NORMAL)
        self.dialogue_text.delete("1.0", tk.END)
        
        dialogue = f"🎤 {npc.name}:\n\n"
        for line in npc.dialogue_lines[:3]:
            dialogue += f"• {line}\n"
        
        self.dialogue_text.insert("1.0", dialogue)
        self.dialogue_text.config(state=tk.DISABLED)
    
    def quick_plant(self, crop_type: str):
        """Quick plant at player position"""
        px, py = int(self.state.player_x), int(self.state.player_y)
        for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            if CropSystem.plant_crop(self.state, px + dx, py + dy, crop_type):
                break
    
    def quick_place(self, building_type: str):
        """Quick place building"""
        px, py = int(self.state.player_x), int(self.state.player_y)
        for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            if BuildingSystem.place_building(self.state, px + dx, py + dy, building_type):
                break
    
    def next_day(self):
        """Advance to next day"""
        self.state.day += 1
        self.state.money += 10
    
    def update_player_movement(self):
        """Update player position based on keys"""
        speed = 100
        delta_time = time.time() - self.last_time
        self.last_time = time.time()
        
        dx, dy = 0, 0
        
        if self.keys_pressed.get("up", False):
            dy -= speed * delta_time
            self.state.player_direction = "up"
        if self.keys_pressed.get("down", False):
            dy += speed * delta_time
            self.state.player_direction = "down"
        if self.keys_pressed.get("left", False):
            dx -= speed * delta_time
            self.state.player_direction = "left"
        if self.keys_pressed.get("right", False):
            dx += speed * delta_time
            self.state.player_direction = "right"
        
        self.state.player_x += dx / self.TILE_SIZE
        self.state.player_y += dy / self.TILE_SIZE
        
        self.state.player_x = max(0, min(self.state.world_width - 1, self.state.player_x))
        self.state.player_y = max(0, min(self.state.world_height - 1, self.state.player_y))
    
    def game_loop(self):
        """Main game loop"""
        if self.running:
            self.update_player_movement()
            CropSystem.update_crops(self.state)
            
            self.render()
            self.update_ui()
            
            self.after(self.FRAME_TIME, self.game_loop)
    
    def render(self):
        """Render game world with actual sprite assets"""
        self.canvas.delete("all")
        self._sprite_refs = []  # Clear old sprites
        
        vp_x = self.state.player_x - self.VIEWPORT_W / 2
        vp_y = self.state.player_y - self.VIEWPORT_H / 2
        
        # Draw grass tiles
        for screen_y in range(self.VIEWPORT_H):
            for screen_x in range(self.VIEWPORT_W):
                world_x = vp_x + screen_x
                world_y = vp_y + screen_y
                
                if 0 <= world_x < self.state.world_width and 0 <= world_y < self.state.world_height:
                    x1 = screen_x * self.TILE_SIZE
                    y1 = screen_y * self.TILE_SIZE
                    x2 = x1 + self.TILE_SIZE
                    y2 = y1 + self.TILE_SIZE
                    
                    # Draw grass background
                    self.canvas.create_rectangle(x1, y1, x2, y2, fill="#228B22", outline="#1a6b1a")
                    self.canvas.create_line(x1, y1, x2, y1, fill="#2a9a2a", width=1)
                    self.canvas.create_line(x1, y1+32, x2, y1+32, fill="#2a9a2a", width=1)
        
        # Draw objects (crops, trees, buildings, NPCs)
        for screen_y in range(self.VIEWPORT_H):
            for screen_x in range(self.VIEWPORT_W):
                world_x = vp_x + screen_x
                world_y = vp_y + screen_y
                
                ix, iy = int(world_x), int(world_y)
                
                if 0 <= ix < self.state.world_width and 0 <= iy < self.state.world_height:
                    x_canvas = screen_x * self.TILE_SIZE + self.TILE_SIZE // 2
                    y_canvas = screen_y * self.TILE_SIZE + self.TILE_SIZE // 2
                    
                    # Draw crops
                    if (ix, iy) in self.state.crops:
                        crop = self.state.crops[(ix, iy)]
                        # Try to get crop sprite
                        sprite = None
                        if crop.crop_type == "potato":
                            sprite = self.assets.sprites.get_sprite("crops", crop.growth_stage, (self.TILE_SIZE, self.TILE_SIZE))
                        
                        if sprite:
                            self.canvas.create_image(x_canvas, y_canvas, image=sprite)
                            self._sprite_refs.append(sprite)
                        else:
                            # Fallback to text representation
                            stage_text = ["🌱", "🌿", "🌾", "✓"][crop.growth_stage]
                            self.canvas.create_text(x_canvas, y_canvas, text=stage_text, font=("Arial", 32))
                    
                    # Draw trees
                    if (ix, iy) in self.state.trees:
                        tree = self.state.trees[(ix, iy)]
                        # Try to get tree sprite
                        sprite = None
                        if tree.tree_type == "whitepine":
                            sprite = self.assets.sprites.get_sprite("trees", 0, (self.TILE_SIZE, self.TILE_SIZE))
                        elif tree.tree_type == "cranberry":
                            sprite = self.assets.sprites.get_sprite("cranberry", 0, (self.TILE_SIZE, self.TILE_SIZE))
                        elif tree.tree_type == "redbaneberry":
                            sprite = self.assets.sprites.get_sprite("redbaneberry", 0, (self.TILE_SIZE, self.TILE_SIZE))
                        
                        if sprite:
                            self.canvas.create_image(x_canvas, y_canvas, image=sprite)
                            self._sprite_refs.append(sprite)
                        else:
                            # Fallback
                            tree_emoji = {"whitepine": "🌲", "cranberry": "🫐", "birch": "🌳", "oak": "🌳"}
                            emoji = tree_emoji.get(tree.tree_type, "🌳")
                            self.canvas.create_text(x_canvas, y_canvas, text=emoji, font=("Arial", 40))
                    
                    # Draw buildings
                    if (ix, iy) in self.state.buildings:
                        building = self.state.buildings[(ix, iy)]
                        building_emoji = {"fence": "🚧", "chest": "🏺", "house": "🏠"}
                        emoji = building_emoji.get(building, "🏗️")
                        self.canvas.create_text(x_canvas, y_canvas, text=emoji, font=("Arial", 36))
                    
                    # Draw NPCs
                    for npc_name, npc in self.state.npcs.items():
                        if npc.x == ix and npc.y == iy:
                            # Draw NPC circle with outline
                            self.canvas.create_oval(
                                x_canvas - 24, y_canvas - 28, x_canvas + 24, y_canvas + 28,
                                fill="#ff6b6b", outline="#cc0000", width=3
                            )
                            # Draw player icon
                            self.canvas.create_text(x_canvas, y_canvas, text="👤", font=("Arial", 26), fill="#000000")
                            # Draw name label
                            self.canvas.create_text(x_canvas, y_canvas - 40, text=npc.name, font=("Arial", 9, "bold"), fill="#000000")
        
        # Draw player sprite
        screen_px = (self.state.player_x - vp_x) * self.TILE_SIZE + self.TILE_SIZE // 2
        screen_py = (self.state.player_y - vp_y) * self.TILE_SIZE + self.TILE_SIZE // 2
        
        # Try to load player sprite from boycat_walkcycle
        player_sprite = self.assets.sprites.get_sprite("player", 0, (self.TILE_SIZE, self.TILE_SIZE))
        
        if player_sprite:
            self.canvas.create_image(int(screen_px), int(screen_py), image=player_sprite)
            self._sprite_refs.append(player_sprite)
        else:
            # Fallback: draw player circle
            self.canvas.create_oval(
                screen_px - 24, screen_py - 28, screen_px + 24, screen_py + 28,
                fill="#6b9dff", outline="#0088ff", width=3
            )
            self.canvas.create_text(screen_px, screen_py, text="🚶", font=("Arial", 32), fill="#000000")
        
        # Draw direction indicator
        direction_indicators = {
            "up": "⬆️", "down": "⬇️", "left": "⬅️", "right": "➡️"
        }
        dir_emoji = direction_indicators.get(self.state.player_direction, "")
        if dir_emoji:
            self.canvas.create_text(screen_px + 28, screen_py - 35, text=dir_emoji, font=("Arial", 16))
    
    def update_ui(self):
        """Update UI labels"""
        self.day_label.config(text=f"Day: {self.state.day}")
        self.money_label.config(text=f"Money: {self.state.money}")
        self.pos_label.config(text=f"Pos: {int(self.state.player_x)}, {int(self.state.player_y)}")
        
        for i in range(8):
            slot = self.state.inventory[i]
            if slot.item:
                text = f"[{i+1}] {slot.item.name} x{slot.amount}"
            else:
                text = f"[{i+1}] Empty"
            
            if i == self.state.selected_slot:
                self.inv_labels[i].config(fg="#00ff00", font=("Arial", 8, "bold"))
            else:
                self.inv_labels[i].config(fg="#aaaaaa", font=("Arial", 8))
            
            self.inv_labels[i].config(text=text)

# ============== WINDOW INTEGRATION ==============

if __name__ == "__main__":
    root = tk.Tk()
    root.title("🌾 Croptopia - Integrated")
    game = CropTopiaGame(root)
    game.pack(fill=tk.BOTH, expand=True)
    root.geometry("1400x700")
    root.mainloop()
