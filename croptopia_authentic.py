"""
CROPTOPIA - 1:1 Recreation from Godot
Authentic 2D RPG top-down pixel art farming game
Featuring Michael View's journey in Shelburne
"""

import tkinter as tk
from tkinter import Canvas, Frame
from PIL import Image, ImageTk
import time
import json
import random
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

# ============== PATHS ==============
WORKSPACE_ROOT = Path(__file__).parent
ASSET_ROOT = Path("C:/Users/F99500/Downloads/Croptopia - 02.11.25")
CROPTOPIA_ASSETS = WORKSPACE_ROOT / "croptopia_assets"

# Try both local and original paths
if not CROPTOPIA_ASSETS.exists():
    CROPTOPIA_ASSETS = ASSET_ROOT

# ============== ASSET LOADER ==============

class AssetCache:
    """Cache for loaded images"""
    def __init__(self):
        self.images: Dict[str, Image.Image] = {}
        self.photo_images: Dict[str, ImageTk.PhotoImage] = {}
        
    def load_image(self, name: str, path: Path) -> Optional[Image.Image]:
        """Load and cache an image"""
        if name not in self.images:
            try:
                if path.exists():
                    self.images[name] = Image.open(path)
                    print(f"✓ Loaded: {name}")
                else:
                    print(f"✗ Missing: {path}")
                    return None
            except Exception as e:
                print(f"Error loading {name}: {e}")
                return None
        return self.images[name]
    
    def get_photo(self, name: str, size: Optional[Tuple[int, int]] = None) -> Optional[ImageTk.PhotoImage]:
        """Get PhotoImage from cache"""
        cache_key = f"{name}_{size[0]}x{size[1]}" if size else name
        
        if cache_key not in self.photo_images and name in self.images:
            img = self.images[name]
            if size:
                img = img.resize(size, Image.Resampling.NEAREST)  # Pixel art scaling
            self.photo_images[cache_key] = ImageTk.PhotoImage(img)
        
        return self.photo_images.get(cache_key)

# ============== GAME DATA ==============

@dataclass
class PlayerData:
    """Michael View's data"""
    position: List[float]
    balance: int = 0
    day: int = 1
    current_month: str = "Monday"
    current_year: int = 2027
    
    # Quest items
    pinecones: int = 0
    sticks: int = 0
    sorrel: int = 0
    redbaneberry: int = 0
    chives: int = 0
    elderberry: int = 0
    
    # Inventory
    inventory_slots: List[Optional[str]] = None
    selected_slot: int = 0
    
    def __post_init__(self):
        if self.inventory_slots is None:
            self.inventory_slots = [None] * 8

@dataclass
class WorldTile:
    """Tile in the world"""
    tile_type: str  # grass, path, water, dirt
    has_tree: bool = False
    tree_type: Optional[str] = None
    has_item: bool = False
    item_type: Optional[str] = None

# ============== WORLD GENERATOR ==============

class WorldGenerator:
    """Generate Croptopia world with proper tiles"""
    
    def __init__(self, width: int = 100, height: int = 100):
        self.width = width
        self.height = height
        self.tiles: Dict[Tuple[int, int], WorldTile] = {}
        
    def generate(self):
        """Generate the world"""
        # Base grass layer
        for x in range(self.width):
            for y in range(self.height):
                self.tiles[(x, y)] = WorldTile(tile_type="grass")
        
        # Add path from spawn
        self._generate_path(50, 50, 60, 50)  # Horizontal path
        self._generate_path(60, 50, 60, 40)  # Vertical path
        
        # Add trees randomly
        self._add_trees(density=0.05)
        
        # Add collectible items
        self._add_items()
        
        print(f"✓ World generated: {self.width}x{self.height} tiles")
        
    def _generate_path(self, x1: int, y1: int, x2: int, y2: int, width: int = 2):
        """Generate a path between two points"""
        # Simple straight path
        if x1 == x2:  # Vertical
            for y in range(min(y1, y2), max(y1, y2) + 1):
                for w in range(-width//2, width//2 + 1):
                    if (x1 + w, y) in self.tiles:
                        self.tiles[(x1 + w, y)].tile_type = "path"
        else:  # Horizontal
            for x in range(min(x1, x2), max(x1, x2) + 1):
                for w in range(-width//2, width//2 + 1):
                    if (x, y1 + w) in self.tiles:
                        self.tiles[(x, y1 + w)].tile_type = "path"
    
    def _add_trees(self, density: float = 0.05):
        """Add trees to the world"""
        tree_types = ["whitepine", "birch", "maple", "spruce", "oak"]
        
        for (x, y), tile in self.tiles.items():
            if tile.tile_type == "grass" and random.random() < density:
                tile.has_tree = True
                tile.tree_type = random.choice(tree_types)
    
    def _add_items(self):
        """Add collectible items to world"""
        item_types = ["pinecones", "sticks", "sorrel", "redbaneberry", "chives", "elderberry"]
        
        # Add 50 random items
        for _ in range(50):
            x = random.randint(0, self.width - 1)
            y = random.randint(0, self.height - 1)
            
            tile = self.tiles.get((x, y))
            if tile and tile.tile_type == "grass" and not tile.has_tree:
                tile.has_item = True
                tile.item_type = random.choice(item_types)

# ============== MAIN GAME ==============

class CroptopiaGame(tk.Frame):
    """Croptopia - Authentic Recreation"""
    
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        
        # Game settings
        self.TILE_SIZE = 64
        self.VIEWPORT_W = 16  # Wider viewport like the real game
        self.VIEWPORT_H = 12
        self.FPS = 60
        self.FRAME_TIME = 1000 // self.FPS
        
        # Asset cache
        self.assets = AssetCache()
        self._sprite_refs = []  # Prevent garbage collection
        
        # Player data
        self.player = PlayerData(
            position=[50.0, 50.0],  # Start at world center
            balance=0,
            day=1,
            current_month="Monday",
            current_year=2027
        )
        
        # World
        self.world = WorldGenerator(width=100, height=100)
        self.world.generate()
        
        # Input
        self.keys_pressed = {}
        self.running = True
        self.last_time = time.time()
        
        # Movement state
        self.current_dir = "down"
        self.velocity = [0.0, 0.0]
        self.speed = 100  # Base speed
        self.can_move = True
        self.wields_axe = False
        
        # Load assets
        self._load_assets()
        
        # Setup UI
        self.setup_ui()
        self.bind_keys()
        
        # Start game loop
        self.after(self.FRAME_TIME, self.game_loop)
    
    def _load_assets(self):
        """Load all game assets"""
        print("Loading assets...")
        
        # Character sprites
        self.assets.load_image("michael_walk", CROPTOPIA_ASSETS / "boycat_walkcycle.png")
        
        # Trees
        self.assets.load_image("whitepine", CROPTOPIA_ASSETS / "whitepine.png")
        self.assets.load_image("birch", CROPTOPIA_ASSETS / "birch_tree.png")
        self.assets.load_image("spruce", CROPTOPIA_ASSETS / "spruce.png")
        
        # Items
        self.assets.load_image("redbaneberry", CROPTOPIA_ASSETS / "redbaneberry.png")
        self.assets.load_image("cranberry", CROPTOPIA_ASSETS / "cranberry.png")
        
        # UI elements
        self.assets.load_image("hotbar", CROPTOPIA_ASSETS / "hotbar_asset.png")
        self.assets.load_image("ui_panel", CROPTOPIA_ASSETS / "game_ui_panel.png")
        
        # Tiles
        self.assets.load_image("grass_tile", CROPTOPIA_ASSETS / "grass_tile_sprite.png")
        self.assets.load_image("path_tile", CROPTOPIA_ASSETS / "path_1x1.png")
        
        print("Assets loaded!")
    
    def setup_ui(self):
        """Setup game canvas and UI"""
        # Main container
        main_frame = Frame(self, bg="#000000")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Game canvas (main view)
        self.canvas = Canvas(
            main_frame,
            width=self.VIEWPORT_W * self.TILE_SIZE,
            height=self.VIEWPORT_H * self.TILE_SIZE,
            bg="#1a3a1a",  # Dark green background
            highlightthickness=0
        )
        self.canvas.pack()
        
        # Overlay UI - Calendar/Date (top-left)
        self.calendar_label = tk.Label(
            self.canvas,
            text=f"{self.player.current_month}\nYear\n{self.player.current_year}",
            bg="#8B6B47",  # Brown background
            fg="#000000",
            font=("Courier", 10, "bold"),
            justify=tk.CENTER,
            padx=10,
            pady=5
        )
        self.canvas.create_window(60, 60, window=self.calendar_label)
        
        # Money display (top-right)
        self.money_label = tk.Label(
            self.canvas,
            text=f"{self.player.balance} $",
            bg="#D4A76A",  # Tan background
            fg="#000000",
            font=("Courier", 16, "bold"),
            padx=15,
            pady=5
        )
        self.canvas.create_window(self.VIEWPORT_W * self.TILE_SIZE - 80, 30, window=self.money_label)
        
        # Debug coords (top-left, small)
        self.coords_label = tk.Label(
            self.canvas,
            text="In scene coords: 50.0",
            bg="#000000",
            fg="#00FF00",
            font=("Courier", 8),
            padx=5
        )
        self.canvas.create_window(100, 10, window=self.coords_label)
        
        # Hotbar at bottom
        hotbar_y = self.VIEWPORT_H * self.TILE_SIZE - 70
        
        # Hotbar background frame
        self.hotbar_frame = Frame(self.canvas, bg="#8B6B47", relief=tk.RAISED, bd=3)
        self.canvas.create_window(self.VIEWPORT_W * self.TILE_SIZE // 2, hotbar_y, window=self.hotbar_frame)
        
        # 8 inventory slots
        self.slot_labels = []
        slot_container = Frame(self.hotbar_frame, bg="#8B6B47")
        slot_container.pack(padx=5, pady=5)
        
        for i in range(8):
            slot = tk.Label(
                slot_container,
                text="",
                bg="#D4A76A" if i == self.player.selected_slot else "#8B6B47",
                fg="#000000",
                font=("Courier", 10),
                width=6,
                height=3,
                relief=tk.SUNKEN,
                bd=2
            )
            slot.grid(row=0, column=i, padx=2)
            self.slot_labels.append(slot)
    
    def bind_keys(self):
        """Bind keyboard controls"""
        self.bind("<KeyPress>", self.on_key_down)
        self.bind("<KeyRelease>", self.on_key_up)
        self.focus_set()
    
    def on_key_down(self, event):
        """Handle key press"""
        key = event.keysym.lower()
        self.keys_pressed[key] = True
        
        # Hotbar selection (1-8)
        if event.char.isdigit() and event.char != '0':
            slot = int(event.char) - 1
            if 0 <= slot < 8:
                self.player.selected_slot = slot
                self.update_hotbar()
        
        # Collect items (Space)
        if key == "space":
            self.collect_nearby_item()
        
        # Interact (E)
        if key == "e":
            pass  # NPC interaction will be added
    
    def on_key_up(self, event):
        """Handle key release"""
        key = event.keysym.lower()
        self.keys_pressed[key] = False
    
    def update_hotbar(self):
        """Update hotbar visual selection"""
        for i, slot in enumerate(self.slot_labels):
            if i == self.player.selected_slot:
                slot.config(bg="#FFD700", relief=tk.RAISED)  # Gold highlight
            else:
                slot.config(bg="#D4A76A", relief=tk.SUNKEN)
    
    def collect_nearby_item(self):
        """Collect items near player"""
        px, py = int(self.player.position[0]), int(self.player.position[1])
        
        # Check 3x3 area around player
        for dx in range(-1, 2):
            for dy in range(-1, 2):
                check_pos = (px + dx, py + dy)
                tile = self.world.tiles.get(check_pos)
                
                if tile and tile.has_item and tile.item_type:
                    # Collect the item
                    item = tile.item_type
                    if item == "pinecones":
                        self.player.pinecones += 1
                    elif item == "sticks":
                        self.player.sticks += 1
                    elif item == "sorrel":
                        self.player.sorrel += 1
                    elif item == "redbaneberry":
                        self.player.redbaneberry += 1
                    elif item == "chives":
                        self.player.chives += 1
                    elif item == "elderberry":
                        self.player.elderberry += 1
                    
                    # Remove from world
                    tile.has_item = False
                    tile.item_type = None
                    print(f"Collected {item}!")
                    return
    
    def update_player_movement(self, delta: float):
        """Update Michael View's movement"""
        if not self.can_move:
            return
        
        dx, dy = 0, 0
        speed = self.speed
        
        # Sprint modifier (Shift key)
        if self.keys_pressed.get("shift_l") or self.keys_pressed.get("shift_r"):
            speed = 200
        
        # 8-directional movement
        moving = False
        
        # Diagonal movement
        if (self.keys_pressed.get("w") or self.keys_pressed.get("up")) and \
           (self.keys_pressed.get("a") or self.keys_pressed.get("left")):
            dy = -50
            dx = -50
            self.current_dir = "up-left"
            moving = True
        elif (self.keys_pressed.get("w") or self.keys_pressed.get("up")) and \
             (self.keys_pressed.get("d") or self.keys_pressed.get("right")):
            dy = -50
            dx = 50
            self.current_dir = "up-right"
            moving = True
        elif (self.keys_pressed.get("s") or self.keys_pressed.get("down")) and \
             (self.keys_pressed.get("a") or self.keys_pressed.get("left")):
            dy = 50
            dx = -50
            self.current_dir = "down-left"
            moving = True
        elif (self.keys_pressed.get("s") or self.keys_pressed.get("down")) and \
             (self.keys_pressed.get("d") or self.keys_pressed.get("right")):
            dy = 50
            dx = 50
            self.current_dir = "down-right"
            moving = True
        
        # Cardinal directions
        elif self.keys_pressed.get("w") or self.keys_pressed.get("up"):
            dy = -speed
            self.current_dir = "up"
            moving = True
        elif self.keys_pressed.get("s") or self.keys_pressed.get("down"):
            dy = speed
            self.current_dir = "down"
            moving = True
        elif self.keys_pressed.get("a") or self.keys_pressed.get("left"):
            dx = -speed
            self.current_dir = "left"
            moving = True
        elif self.keys_pressed.get("d") or self.keys_pressed.get("right"):
            dx = speed
            self.current_dir = "right"
            moving = True
        
        # Apply movement
        self.velocity = [dx, dy]
        self.player.position[0] += dx * delta
        self.player.position[1] += dy * delta
        
        # Clamp to world bounds
        self.player.position[0] = max(0, min(self.world.width - 1, self.player.position[0]))
        self.player.position[1] = max(0, min(self.world.height - 1, self.player.position[1]))
    
    def game_loop(self):
        """Main game loop"""
        if self.running:
            current_time = time.time()
            delta = current_time - self.last_time
            self.last_time = current_time
            
            # Update
            self.update_player_movement(delta)
            
            # Render
            self.render()
            self.update_ui()
            
            # Schedule next frame
            self.after(self.FRAME_TIME, self.game_loop)
    
    def render(self):
        """Render the game world"""
        self.canvas.delete("game")  # Delete game objects, keep UI
        self._sprite_refs = []
        
        # Calculate viewport centered on player
        vp_x = self.player.position[0] - self.VIEWPORT_W / 2
        vp_y = self.player.position[1] - self.VIEWPORT_H / 2
        
        vp_x = max(0, min(self.world.width - self.VIEWPORT_W, vp_x))
        vp_y = max(0, min(self.world.height - self.VIEWPORT_H, vp_y))
        
        # Render tiles
        for sy in range(self.VIEWPORT_H + 1):
            for sx in range(self.VIEWPORT_W + 1):
                world_x = int(vp_x + sx)
                world_y = int(vp_y + sy)
                
                tile = self.world.tiles.get((world_x, world_y))
                if not tile:
                    continue
                
                screen_x = sx * self.TILE_SIZE
                screen_y = sy * self.TILE_SIZE
                
                # Draw tile background
                if tile.tile_type == "grass":
                    # Varied grass colors for texture
                    color = ["#2a5a2a", "#258525", "#2a6a2a", "#236623"][(world_x + world_y) % 4]
                    self.canvas.create_rectangle(
                        screen_x, screen_y, 
                        screen_x + self.TILE_SIZE, screen_y + self.TILE_SIZE,
                        fill=color, outline="#1a4a1a", width=1, tags="game"
                    )
                elif tile.tile_type == "path":
                    # Brown path
                    self.canvas.create_rectangle(
                        screen_x, screen_y,
                        screen_x + self.TILE_SIZE, screen_y + self.TILE_SIZE,
                        fill="#8B6B47", outline="#6B4B27", width=1, tags="game"
                    )
                
                # Draw trees
                if tile.has_tree and tile.tree_type:
                    tree_img = self.assets.get_photo(tile.tree_type, (self.TILE_SIZE, self.TILE_SIZE * 2))
                    if tree_img:
                        self.canvas.create_image(
                            screen_x + self.TILE_SIZE // 2,
                            screen_y + self.TILE_SIZE,
                            image=tree_img, tags="game"
                        )
                        self._sprite_refs.append(tree_img)
                    else:
                        # Fallback tree representation
                        self.canvas.create_oval(
                            screen_x + 10, screen_y - 20,
                            screen_x + self.TILE_SIZE - 10, screen_y + 40,
                            fill="#2d5016", outline="#1a3010", width=2, tags="game"
                        )
                        self.canvas.create_rectangle(
                            screen_x + self.TILE_SIZE // 2 - 8, screen_y + 20,
                            screen_x + self.TILE_SIZE // 2 + 8, screen_y + self.TILE_SIZE,
                            fill="#5a3a1a", outline="#3a2a0a", width=1, tags="game"
                        )
                
                # Draw collectible items
                if tile.has_item and tile.item_type:
                    # Colorful pixels for items
                    item_colors = {
                        "pinecones": "#8B4513",
                        "sticks": "#A0522D",
                        "sorrel": "#90EE90",
                        "redbaneberry": "#FF1493",
                        "chives": "#32CD32",
                        "elderberry": "#8B008B"
                    }
                    color = item_colors.get(tile.item_type, "#FFFF00")
                    
                    # Draw as small colorful squares (like in screenshot)
                    item_x = screen_x + self.TILE_SIZE // 2
                    item_y = screen_y + self.TILE_SIZE // 2
                    
                    for i in range(3):  # 3 small squares
                        ox = random.randint(-8, 8)
                        oy = random.randint(-8, 8)
                        self.canvas.create_rectangle(
                            item_x + ox - 3, item_y + oy - 3,
                            item_x + ox + 3, item_y + oy + 3,
                            fill=color, outline="#000000", width=1, tags="game"
                        )
        
        # Draw Michael View (player)
        screen_x = (self.player.position[0] - vp_x) * self.TILE_SIZE
        screen_y = (self.player.position[1] - vp_y) * self.TILE_SIZE
        
        # Try to load Michael's sprite
        michael_sprite = self.assets.get_photo("michael_walk", (self.TILE_SIZE, self.TILE_SIZE))
        if michael_sprite:
            self.canvas.create_image(
                int(screen_x), int(screen_y),
                image=michael_sprite, tags="game"
            )
            self._sprite_refs.append(michael_sprite)
        else:
            # Fallback character (pixel art style)
            # Head
            self.canvas.create_oval(
                screen_x - 12, screen_y - 28,
                screen_x + 12, screen_y - 8,
                fill="#FFD1A8", outline="#000000", width=2, tags="game"
            )
            # Eyes
            self.canvas.create_rectangle(
                screen_x - 8, screen_y - 22,
                screen_x - 4, screen_y - 18,
                fill="#000000", tags="game"
            )
            self.canvas.create_rectangle(
                screen_x + 4, screen_y - 22,
                screen_x + 8, screen_y - 18,
                fill="#000000", tags="game"
            )
            # Body
            self.canvas.create_rectangle(
                screen_x - 14, screen_y - 8,
                screen_x + 14, screen_y + 16,
                fill="#654321", outline="#000000", width=2, tags="game"
            )
            # Legs
            self.canvas.create_rectangle(
                screen_x - 12, screen_y + 16,
                screen_x - 4, screen_y + 32,
                fill="#4A3212", outline="#000000", width=1, tags="game"
            )
            self.canvas.create_rectangle(
                screen_x + 4, screen_y + 16,
                screen_x + 12, screen_y + 32,
                fill="#4A3212", outline="#000000", width=1, tags="game"
            )
    
    def update_ui(self):
        """Update UI elements"""
        # Update calendar
        self.calendar_label.config(text=f"{self.player.current_month}\nYear\n{self.player.current_year}")
        
        # Update money
        self.money_label.config(text=f"{self.player.balance} $")
        
        # Update coords
        self.coords_label.config(text=f"In scene coords: {self.player.position[0]:.1f}")
        
        # Update hotbar slots with quest items
        quest_items = [
            f"🌲{self.player.pinecones}",
            f"🪵{self.player.sticks}",
            f"🌿{self.player.sorrel}",
            f"🔴{self.player.redbaneberry}",
            f"🌱{self.player.chives}",
            f"🫐{self.player.elderberry}",
            "", ""
        ]
        
        for i, slot in enumerate(self.slot_labels):
            slot.config(text=quest_items[i])

# ============== WINDOW INTEGRATION ==============

if __name__ == "__main__":
    root = tk.Tk()
    root.title("🌾 Croptopia (DEBUG)")
    root.configure(bg="#000000")
    game = CroptopiaGame(root)
    game.pack(fill=tk.BOTH, expand=True)
    root.geometry("1024x768")
    root.mainloop()
