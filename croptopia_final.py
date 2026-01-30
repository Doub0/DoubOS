"""
CROPTOPIA - EXACT 1:1 Recreation from Godot TSCN Files
Based on actual .tscn node structure and sprite configurations  
Michael View's farming journey in Shelburne
"""

import tkinter as tk
from tkinter import Canvas, Frame, Label
from PIL import Image, ImageTk
import time
import random
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

# ============== ASSET PATHS ==============
ASSET_ROOT = Path("C:/Users/F99500/Downloads/Croptopia - 02.11.25/assets")

# ============== SPRITE LOADER (From TSCN Atlas Data) ==============

class SpriteAtlas:
    """Load sprites using atlas regions from TSCN files"""
    def __init__(self):
        self.atlases: Dict[str, Image.Image] = {}
        self.frames: Dict[str, List[ImageTk.PhotoImage]] = {}
        self._refs = []  # Prevent GC
        
    def load_atlas(self, name: str, path: Path):
        """Load a sprite atlas"""
        try:
            if path.exists():
                self.atlases[name] = Image.open(path).convert("RGBA")
                print(f"✓ Loaded atlas: {name}")
                return True
        except Exception as e:
            print(f"✗ Failed to load {name}: {e}")
        return False
    
    def extract_frames(self, atlas_name: str, animation_name: str, regions: List[Tuple[int, int, int, int]], scale: int = 4):
        """Extract animation frames from atlas using region data from TSCN"""
        if atlas_name not in self.atlases:
            return []
        
        atlas = self.atlases[atlas_name]
        frames = []
        
        for region in regions:
            x, y, w, h = region
            try:
                frame_img = atlas.crop((x, y, x + w, y + h))
                scaled = frame_img.resize((w * scale, h * scale), Image.Resampling.NEAREST)
                photo = ImageTk.PhotoImage(scaled)
                frames.append(photo)
                self._refs.append(photo)
            except Exception as e:
                print(f"Error extracting frame: {e}")
        
        if frames:
            self.frames[animation_name] = frames
            print(f"✓ {animation_name}: {len(frames)} frames")
        
        return frames

# ============== PLAYER DATA ==============

@dataclass
class PlayerData:
    """Michael View's character data"""
    position: List[float]
    velocity: List[float]
    balance: int = 0
    speed: int = 100
    inventory_slots: List[Optional[str]] = None
    selected_slot: int = 0
    pinecones: int = 0
    sticks: int = 0
    sorrel: int = 0
    redbaneberry: int = 0
    chives: int = 0
    elderberry: int = 0
    current_dir: str = "down"
    can_move: bool = True
    
    def __post_init__(self):
        if self.inventory_slots is None:
            self.inventory_slots = [None] * 8

# ============== MAIN GAME ==============

class CroptopiaGame(tk.Frame):
    """Croptopia - 1:1 Recreation from TSCN"""
    
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        
        # Settings from player.tscn Camera2D
        self.TILE_SIZE = 64
        self.VIEWPORT_W = 18
        self.VIEWPORT_H = 12
        self.FPS = 60
        self.FRAME_TIME = 1000 // self.FPS
        
        # Sprite loader
        self.sprites = SpriteAtlas()
        
        # Player from player.tscn (position Vector2(12, -11))
        self.player = PlayerData(
            position=[12.0, -11.0],
            velocity=[0.0, 0.0],
            speed=100
        )
        
        # Animation
        self.current_animation = "walk_down_idle"
        self.animation_frame = 0
        self.animation_time = 0.0
        self.animation_speed = 5.0
        
        # Input
        self.keys_pressed = {}
        self.running = True
        self.last_time = time.time()
        
        # UI data
        self.current_day = "Monday"
        self.current_year = 2027
        self.in_scene_coords = 33.4
        
        # Load assets from TSCN
        self._load_assets_from_tscn()
        
        # Setup UI
        self.setup_ui()
        self.bind_keys()
        
        # Start
        self.after(self.FRAME_TIME, self.game_loop)
    
    def _load_assets_from_tscn(self):
        """Load based on TSCN references"""
        print("Loading from TSCN...")
        
        # From player_anim.tres - character_sprites_1.png
        if self.sprites.load_atlas("character_sprites", ASSET_ROOT / "character_sprites_1.png"):
            # Exact atlas regions from player_anim.tres
            self.sprites.extract_frames("character_sprites", "walk_down", [
                (16, 0, 16, 36), (0, 0, 16, 36), (48, 0, 16, 36), (32, 0, 16, 36)
            ])
            self.sprites.extract_frames("character_sprites", "walk_down_idle", [
                (376, 0, 16, 36), (392, 0, 16, 36), (408, 0, 16, 36)
            ])
            self.sprites.extract_frames("character_sprites", "walk_up", [
                (64, 0, 16, 36), (80, 0, 16, 36), (96, 0, 16, 36), (112, 0, 16, 36)
            ])
            self.sprites.extract_frames("character_sprites", "walk_left", [
                (143, 0, 14, 36), (127, 0, 14, 36), (175, 0, 14, 36), (159, 0, 14, 36)
            ])
            self.sprites.extract_frames("character_sprites", "walk_right", [
                (143, 0, 14, 36), (127, 0, 14, 36), (175, 0, 14, 36), (159, 0, 14, 36)
            ])
        
        print("Assets loaded!")
    
    def setup_ui(self):
        """UI from game_ui.tscn"""
        self.canvas = Canvas(
            self,
            width=self.VIEWPORT_W * self.TILE_SIZE,
            height=self.VIEWPORT_H * self.TILE_SIZE,
            bg="#2a5a2a",
            highlightthickness=0
        )
        self.canvas.pack()
        
        # Calendar (from game_ui.tscn Panel offset 41,40)
        cal_frame = Frame(self.canvas, bg="#8B6B47", relief=tk.RAISED, bd=2)
        self.canvas.create_window(70, 70, window=cal_frame)
        Label(cal_frame, text="Monday", bg="#8B6B47", fg="#000000", 
              font=("Arial", 9, "bold")).pack(padx=8, pady=2)
        Label(cal_frame, text="Year", bg="#8B6B47", fg="#000000", 
              font=("Arial", 8)).pack()
        self.year_label = Label(cal_frame, text="2027", bg="#8B6B47", fg="#000000", 
                               font=("Arial", 9, "bold"))
        self.year_label.pack(padx=8, pady=2)
        
        # Money (from game_ui.tscn offset 1090,40)
        money_frame = Frame(self.canvas, bg="#D4A76A", relief=tk.RAISED, bd=2)
        self.canvas.create_window(self.VIEWPORT_W * self.TILE_SIZE - 100, 50, window=money_frame)
        self.money_label = Label(money_frame, text="0 $", bg="#D4A76A", fg="#000000", 
                                font=("Arial", 14, "bold"))
        self.money_label.pack(padx=15, pady=8)
        
        # Debug coords
        self.coords_label = Label(self.canvas, text="In scene coords: 33.4", 
                                 bg="#000000", fg="#00FF00", font=("Courier", 8))
        self.canvas.create_window(100, 10, window=self.coords_label)
        
        # Hotbar (bottom)
        hotbar_y = self.VIEWPORT_H * self.TILE_SIZE - 80
        hotbar_container = Frame(self.canvas, bg="#8B6B47", relief=tk.RAISED, bd=4)
        self.canvas.create_window(self.VIEWPORT_W * self.TILE_SIZE // 2, hotbar_y, window=hotbar_container)
        
        slots_frame = Frame(hotbar_container, bg="#8B6B47")
        slots_frame.pack(padx=4, pady=4)
        
        self.slot_labels = []
        for i in range(8):
            slot = Label(slots_frame, text="", bg="#D4A76A", fg="#000000",
                        font=("Arial", 10), width=7, height=3, relief=tk.SUNKEN, bd=3)
            slot.grid(row=0, column=i, padx=2)
            self.slot_labels.append(slot)
        
        self.slot_labels[0].config(relief=tk.RAISED, bd=4, bg="#FFD700")
    
    def bind_keys(self):
        self.bind("<KeyPress>", self.on_key_down)
        self.bind("<KeyRelease>", self.on_key_up)
        self.focus_set()
    
    def on_key_down(self, event):
        key = event.keysym.lower()
        self.keys_pressed[key] = True
        
        if event.char.isdigit() and event.char != '0':
            slot = int(event.char) - 1
            if 0 <= slot < 8:
                self.player.selected_slot = slot
                self.update_hotbar_selection()
        
        if key == "space":
            self.collect_nearby_item()
    
    def on_key_up(self, event):
        key = event.keysym.lower()
        self.keys_pressed[key] = False
    
    def update_hotbar_selection(self):
        for i, slot in enumerate(self.slot_labels):
            if i == self.player.selected_slot:
                slot.config(relief=tk.RAISED, bd=4, bg="#FFD700")
            else:
                slot.config(relief=tk.SUNKEN, bd=3, bg="#D4A76A")
    
    def collect_nearby_item(self):
        items = ["pinecones", "sticks", "sorrel", "redbaneberry", "chives", "elderberry"]
        item = random.choice(items)
        amount = random.randint(1, 3)
        
        if item == "pinecones":
            self.player.pinecones += amount
        elif item == "sticks":
            self.player.sticks += amount
        elif item == "sorrel":
            self.player.sorrel += amount
        elif item == "redbaneberry":
            self.player.redbaneberry += amount
        elif item == "chives":
            self.player.chives += amount
        elif item == "elderberry":
            self.player.elderberry += amount
        
        print(f"Collected {amount}x {item}!")
    
    def update_player_movement(self, delta: float):
        """From player.gd player_move()"""
        if not self.player.can_move:
            return
        
        dx, dy = 0, 0
        speed = self.player.speed
        moving = False
        
        if self.keys_pressed.get("shift_l") or self.keys_pressed.get("shift_r"):
            speed = 200
        
        # Diagonals (50 px/s from player.gd)
        if (self.keys_pressed.get("up") or self.keys_pressed.get("w")) and \
           (self.keys_pressed.get("left") or self.keys_pressed.get("a")):
            dy, dx = -50, -50
            self.current_animation = "walk_left"
            moving = True
        elif (self.keys_pressed.get("up") or self.keys_pressed.get("w")) and \
             (self.keys_pressed.get("right") or self.keys_pressed.get("d")):
            dy, dx = -50, 50
            self.current_animation = "walk_right"
            moving = True
        elif (self.keys_pressed.get("down") or self.keys_pressed.get("s")) and \
             (self.keys_pressed.get("left") or self.keys_pressed.get("a")):
            dy, dx = 50, -50
            self.current_animation = "walk_left"
            moving = True
        elif (self.keys_pressed.get("down") or self.keys_pressed.get("s")) and \
             (self.keys_pressed.get("right") or self.keys_pressed.get("d")):
            dy, dx = 50, 50
            self.current_animation = "walk_right"
            moving = True
        # Cardinals
        elif self.keys_pressed.get("up") or self.keys_pressed.get("w"):
            dy = -speed
            self.current_animation = "walk_up"
            moving = True
        elif self.keys_pressed.get("down") or self.keys_pressed.get("s"):
            dy = speed
            self.current_animation = "walk_down"
            moving = True
        elif self.keys_pressed.get("left") or self.keys_pressed.get("a"):
            dx = -speed
            self.current_animation = "walk_left"
            moving = True
        elif self.keys_pressed.get("right") or self.keys_pressed.get("d"):
            dx = speed
            self.current_animation = "walk_right"
            moving = True
        
        if not moving:
            self.current_animation = "walk_down_idle"
            self.player.velocity = [0, 0]
        else:
            self.player.velocity = [dx, dy]
        
        self.player.position[0] += dx * delta
        self.player.position[1] += dy * delta
    
    def update_animation(self, delta: float):
        self.animation_time += delta
        frames = self.sprites.frames.get(self.current_animation, [])
        if not frames:
            return
        
        frame_duration = 1.0 / self.animation_speed
        if self.animation_time >= frame_duration:
            self.animation_time = 0
            self.animation_frame = (self.animation_frame + 1) % len(frames)
    
    def game_loop(self):
        if self.running:
            current_time = time.time()
            delta = current_time - self.last_time
            self.last_time = current_time
            
            self.update_player_movement(delta)
            self.update_animation(delta)
            self.render()
            self.update_ui()
            
            self.after(self.FRAME_TIME, self.game_loop)
    
    def render(self):
        self.canvas.delete("game")
        
        cam_x = self.player.position[0]
        cam_y = self.player.position[1]
        
        # Grass tiles
        for sy in range(self.VIEWPORT_H + 1):
            for sx in range(self.VIEWPORT_W + 1):
                world_x = int(cam_x - self.VIEWPORT_W / 2 + sx)
                world_y = int(cam_y - self.VIEWPORT_H / 2 + sy)
                
                screen_x = sx * self.TILE_SIZE
                screen_y = sy * self.TILE_SIZE
                
                grass_colors = ["#2a5a2a", "#258525", "#2a6a2a", "#236623"]
                color = grass_colors[(world_x + world_y) % 4]
                
                self.canvas.create_rectangle(
                    screen_x, screen_y,
                    screen_x + self.TILE_SIZE, screen_y + self.TILE_SIZE,
                    fill=color, outline="#1a4a1a", width=1, tags="game"
                )
        
        # Michael View (center)
        screen_x = (self.VIEWPORT_W / 2) * self.TILE_SIZE
        screen_y = (self.VIEWPORT_H / 2) * self.TILE_SIZE
        
        # Get animation frame
        frames = self.sprites.frames.get(self.current_animation, [])
        if frames and self.animation_frame < len(frames):
            sprite = frames[self.animation_frame]
            self.canvas.create_image(int(screen_x), int(screen_y), image=sprite, tags="game")
        else:
            # Fallback pixel art Michael
            self.canvas.create_oval(screen_x - 16, screen_y - 48, screen_x + 16, screen_y - 24,
                                   fill="#FFD1A8", outline="#000000", width=2, tags="game")
            self.canvas.create_rectangle(screen_x - 10, screen_y - 42, screen_x - 6, screen_y - 38,
                                        fill="#000000", tags="game")
            self.canvas.create_rectangle(screen_x + 6, screen_y - 42, screen_x + 10, screen_y - 38,
                                        fill="#000000", tags="game")
            self.canvas.create_rectangle(screen_x - 20, screen_y - 24, screen_x + 20, screen_y + 16,
                                        fill="#654321", outline="#000000", width=2, tags="game")
            self.canvas.create_rectangle(screen_x - 16, screen_y + 16, screen_x - 6, screen_y + 48,
                                        fill="#4A3212", outline="#000000", width=1, tags="game")
            self.canvas.create_rectangle(screen_x + 6, screen_y + 16, screen_x + 16, screen_y + 48,
                                        fill="#4A3212", outline="#000000", width=1, tags="game")
        
        # Shadow (from player.tscn)
        shadow_y = 52
        self.canvas.create_oval(screen_x - 20, screen_y + shadow_y - 8, screen_x + 20, screen_y + shadow_y + 8,
                               fill="#000000", outline="", tags="game", stipple="gray50")
    
    def update_ui(self):
        self.money_label.config(text=f"{self.player.balance} $")
        self.coords_label.config(text=f"In scene coords: {self.in_scene_coords:.1f}")
        
        quest_display = [
            f"🌲\n{self.player.pinecones}",
            f"🪵\n{self.player.sticks}",
            f"🌿\n{self.player.sorrel}",
            f"🔴\n{self.player.redbaneberry}",
            f"🌱\n{self.player.chives}",
            f"🫐\n{self.player.elderberry}",
            "", ""
        ]
        
        for i, slot in enumerate(self.slot_labels):
            slot.config(text=quest_display[i])

if __name__ == "__main__":
    root = tk.Tk()
    root.title("🌾 Croptopia (DEBUG)")
    root.configure(bg="#000000")
    game = CroptopiaGame(root)
    game.pack(fill=tk.BOTH, expand=True)
    root.geometry("1152x768")
    root.mainloop()
