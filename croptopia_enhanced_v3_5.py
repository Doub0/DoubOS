"""
DoubOS - Ultimate Croptopia v3.5 - Asset-Enhanced Edition
Features viewport system, player movement, and asset integration
"""

import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import os
import json
import random


class CropData:
    """Crop characteristics with asset references"""
    CROPS = {
        "🌿 Chives": {
            "seed_cost": 20,
            "sell_price": 35,
            "growth_days": 5,
            "energy_cost": 3,
            "emoji": "🌿",
            "color": "#8bc34a",
            "asset_ref": "chives"
        },
        "🌾 Wheat": {
            "seed_cost": 5,
            "sell_price": 12,
            "growth_days": 2,
            "energy_cost": 1,
            "emoji": "🌾",
            "color": "#cddc39",
            "asset_ref": "wheat"
        },
        "🥕 Carrot": {
            "seed_cost": 10,
            "sell_price": 18,
            "growth_days": 3,
            "energy_cost": 1,
            "emoji": "🥕",
            "color": "#ff9800",
            "asset_ref": "carrot"
        },
        "🥔 Potato": {
            "seed_cost": 12,
            "sell_price": 20,
            "growth_days": 3,
            "energy_cost": 2,
            "emoji": "🥔",
            "color": "#a1887f",
            "asset_ref": "potato"
        },
        "🍎 Apple": {
            "seed_cost": 15,
            "sell_price": 25,
            "growth_days": 4,
            "energy_cost": 2,
            "emoji": "🍎",
            "color": "#f44336",
            "asset_ref": "apple"
        },
        "🍀 Sorrel": {
            "seed_cost": 25,
            "sell_price": 42,
            "growth_days": 6,
            "energy_cost": 3,
            "emoji": "🍀",
            "color": "#4caf50",
            "asset_ref": "sorrel"
        },
        "🍓 Cranberry": {
            "seed_cost": 30,
            "sell_price": 55,
            "growth_days": 7,
            "energy_cost": 4,
            "emoji": "🍓",
            "color": "#e91e63",
            "asset_ref": "cranberry"
        },
        "🫐 Elderberry": {
            "seed_cost": 28,
            "sell_price": 50,
            "growth_days": 6,
            "energy_cost": 3,
            "emoji": "🫐",
            "color": "#673ab7",
            "asset_ref": "elderberry"
        },
        "❤️ Redbaneberry": {
            "seed_cost": 22,
            "sell_price": 40,
            "growth_days": 5,
            "energy_cost": 3,
            "emoji": "❤️",
            "color": "#c2185b",
            "asset_ref": "redbaneberry"
        },
        "🌰 Apricorn": {
            "seed_cost": 18,
            "sell_price": 32,
            "growth_days": 4,
            "energy_cost": 2,
            "emoji": "🌰",
            "color": "#ff6f00",
            "asset_ref": "apricorn"
        }
    }
    
    # Asset manifest for reference
    AVAILABLE_ASSETS = {
        "backgrounds": ["grass_tile_sprite.png", "colored_grass_tile_spritesheet.png", "grass_corner_tile.png"],
        "buildings": ["buildings_1.png"],
        "characters": ["character_sprites_1.png", "zea_spritesheet.png", "brock_sprite_sheet.png"],
        "items": ["coal_item.png", "raw_iron_item.png", "flint.png"],
        "ui": ["hotbar_asset.png", "game_ui_panel.png", "ui_bar.png"],
        "trees": ["birch_tree.png", "maple_tree.png", "white_pine.png", "sweet_gum_tree.png"],
        "water": ["water_tiles_2.png", "water_sprite_sheet.png"]
    }


class GameState:
    """Enhanced game state with asset awareness"""
    
    def __init__(self):
        self.money = 500
        self.day = 1
        self.season = "Spring"
        self.temperature = 70
        self.max_energy = 100
        self.energy = 100
        self.farm = {}
        self.inventory = {}
        self.hotbar = {}
        self.current_tool = "plant"
        self.selected_crop = None
        self.playtime_minutes = 0
        self.buildings = {}
        self.npcs = {}
        self.events = []
        self.relationships = {}
        
        # Player state
        self.player_x = 6
        self.player_y = 6
        
        # Asset tracking
        self.asset_cache = {}
        self.asset_folder = "C:\\Users\\F99500\\Downloads\\Croptopia - 02.11.25\\assets"
        
        # Initialize hotbar
        for i in range(1, 9):
            self.hotbar[i] = None
            
        # Initialize inventory
        for crop_name in CropData.CROPS:
            self.inventory[crop_name] = 0
        self.inventory["Stick"] = 5
        self.inventory["Flint"] = 3
        self.inventory["Wood"] = 0
        self.inventory["Stone"] = 0
        self.inventory["Coal"] = 0
        self.inventory["Iron Ore"] = 0
        
        # Initialize farm
        for x in range(12):
            for y in range(12):
                self.farm[(x, y)] = {
                    "plant": None,
                    "growth": 0,
                    "watered": False,
                    "age": 0,
                    "quality": 1.0
                }
        
        self.init_npcs()
        self.check_special_events()
    
    def move_player(self, dx, dy):
        """Move player"""
        new_x = max(0, min(11, self.player_x + dx))
        new_y = max(0, min(11, self.player_y + dy))
        
        if (new_x, new_y) != (self.player_x, self.player_y):
            self.player_x = new_x
            self.player_y = new_y
            return True
        return False
    
    def get_season(self):
        """Get current season"""
        cycle = (self.day - 1) // 28
        seasons = ["Spring", "Summer", "Fall", "Winter"]
        return seasons[cycle % 4]
    
    def update_temperature(self):
        """Update temperature"""
        season = self.get_season()
        temps = {"Spring": 65, "Summer": 85, "Fall": 60, "Winter": 35}
        self.temperature = temps.get(season, 70) + random.randint(-10, 10)
    
    def init_npcs(self):
        """Initialize NPCs"""
        self.npcs = {
            "Zea": {
                "location": (3, 3),
                "dialogue": "Hello! How's your farming going?",
                "schedule": "morning",
                "relationship": 0,
                "asset_ref": "zea_spritesheet.png"
            },
            "Philip": {
                "location": (2, 5),
                "dialogue": "Welcome to the shop!",
                "schedule": "always",
                "relationship": 0,
                "asset_ref": "phillip_tool_shop.png"
            },
            "Leo": {
                "location": (9, 9),
                "dialogue": "Interesting times ahead...",
                "schedule": "afternoon",
                "relationship": 0,
                "asset_ref": "leo_story.png"
            },
            "Brock": {
                "location": (10, 2),
                "dialogue": "Stay out of trouble.",
                "schedule": "always",
                "relationship": 0,
                "asset_ref": "brock_sprite_sheet.png"
            }
        }
    
    def check_special_events(self):
        """Check for events"""
        if self.day % 20 == 0 and self.day > 0:
            self.events.append({
                "type": "raid",
                "name": "Lunar Crusader Raid",
                "day": self.day,
                "reward": 100
            })
        if self.day % 28 == 0 and self.day > 0:
            self.events.append({
                "type": "speech",
                "name": "Mayor's Speech",
                "day": self.day,
                "text": "The community is thriving!"
            })
    
    def add_building(self, x, y, building_type):
        """Add building"""
        if (x, y) not in self.buildings:
            self.buildings[(x, y)] = {
                "type": building_type,
                "built_day": self.day,
                "condition": 100
            }
            return True
        return False
    
    def get_building_cost(self, building_type):
        """Get building cost"""
        costs = {"fence": 50, "chest": 75, "shed": 200, "greenhouse": 400}
        return costs.get(building_type, 100)
    
    def consume_energy(self, amount):
        """Use energy"""
        self.energy = max(0, self.energy - amount)
        return self.energy > 0
    
    def rest(self):
        """Rest"""
        self.energy = min(self.max_energy, self.energy + 30)
        self.day += 1
    
    def new_day(self):
        """New day"""
        self.day += 1
        self.season = self.get_season()
        for pos, cell in self.farm.items():
            if cell["plant"] and cell["growth"] < 100:
                cell["growth"] = min(100, cell["growth"] + 20)
            if cell["watered"]:
                cell["watered"] = False
    
    def get_asset_path(self, asset_name):
        """Get full asset path"""
        return os.path.join(self.asset_folder, asset_name)
    
    def asset_exists(self, asset_name):
        """Check if asset exists"""
        path = self.get_asset_path(asset_name)
        return os.path.exists(path)


class UltimatecroptopiaGame(tk.Frame):
    """v3.5 - Asset-Enhanced Version"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.parent = parent
        self.state = GameState()
        self.cell_size = 40
        self.viewport_width = 12
        self.viewport_height = 10
        self.keys_pressed = set()
        self.photo_images = {}  # Cache for PhotoImage objects
        
        self.setup_ui()
        self.bind_keys()
        self.update_game_loop()
        self.update_display()
        
    def setup_ui(self):
        """Create UI"""
        self.configure(bg="#1e1e2e")
        
        # TOP BAR
        top_bar = tk.Frame(self, bg="#313244", height=60)
        top_bar.pack(fill=tk.X, padx=5, pady=5)
        top_bar.pack_propagate(False)
        
        self.day_label = tk.Label(top_bar, text="", font=("Arial", 11, "bold"), bg="#313244", fg="#89b4fa")
        self.day_label.pack(side=tk.LEFT, padx=10, pady=5)
        
        self.season_label = tk.Label(top_bar, text="", font=("Arial", 11, "bold"), bg="#313244", fg="#a6e3a1")
        self.season_label.pack(side=tk.LEFT, padx=10, pady=5)
        
        self.temp_label = tk.Label(top_bar, text="", font=("Arial", 11, "bold"), bg="#313244", fg="#fab387")
        self.temp_label.pack(side=tk.LEFT, padx=10, pady=5)
        
        self.money_label = tk.Label(top_bar, text="", font=("Arial", 11, "bold"), bg="#313244", fg="#f38ba8")
        self.money_label.pack(side=tk.RIGHT, padx=10, pady=5)
        
        self.energy_label = tk.Label(top_bar, text="", font=("Arial", 11, "bold"), bg="#313244", fg="#f9e2af")
        self.energy_label.pack(side=tk.RIGHT, padx=10, pady=5)
        
        # ASSET INFO
        asset_info = tk.Label(top_bar, text="Asset Folder: Available", font=("Arial", 8), bg="#313244", fg="#89dceb")
        asset_info.pack(side=tk.LEFT, padx=10, pady=5)
        
        # MAIN GAME AREA
        main_frame = tk.Frame(self, bg="#1e1e2e")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # LEFT PANEL - TOOLS
        left_panel = tk.Frame(main_frame, bg="#313244", width=150)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=5)
        left_panel.pack_propagate(False)
        
        tk.Label(left_panel, text="🛠️ TOOLS", font=("Arial", 10, "bold"), bg="#313244", fg="#89dceb").pack(pady=5)
        
        tool_frame = tk.Frame(left_panel, bg="#313244")
        tool_frame.pack(fill=tk.X, padx=5, pady=5)
        
        tk.Button(tool_frame, text="🌱 Plant", font=("Arial", 9), command=lambda: self.select_action("plant"),
                 bg="#45475a", fg="#cdd6f4", relief=tk.FLAT).pack(pady=2, fill=tk.X)
        tk.Button(tool_frame, text="💧 Water", font=("Arial", 9), command=lambda: self.select_action("water"),
                 bg="#45475a", fg="#cdd6f4", relief=tk.FLAT).pack(pady=2, fill=tk.X)
        tk.Button(tool_frame, text="✂️ Harvest", font=("Arial", 9), command=lambda: self.select_action("harvest"),
                 bg="#45475a", fg="#cdd6f4", relief=tk.FLAT).pack(pady=2, fill=tk.X)
        tk.Button(tool_frame, text="🗑️ Clear", font=("Arial", 9), command=lambda: self.select_action("clear"),
                 bg="#45475a", fg="#cdd6f4", relief=tk.FLAT).pack(pady=2, fill=tk.X)
        
        tk.Label(left_panel, text="🏗️ BUILD", font=("Arial", 10, "bold"), bg="#313244", fg="#89dceb").pack(pady=(10, 5))
        
        build_frame = tk.Frame(left_panel, bg="#313244")
        build_frame.pack(fill=tk.X, padx=5, pady=5)
        
        tk.Button(build_frame, text="🚧 Fence $50", font=("Arial", 8), command=lambda: self.place_building("fence"),
                 bg="#45475a", fg="#cdd6f4", relief=tk.FLAT).pack(pady=2, fill=tk.X)
        tk.Button(build_frame, text="📦 Chest $75", font=("Arial", 8), command=lambda: self.place_building("chest"),
                 bg="#45475a", fg="#cdd6f4", relief=tk.FLAT).pack(pady=2, fill=tk.X)
        tk.Button(build_frame, text="🏠 Shed $200", font=("Arial", 8), command=lambda: self.place_building("shed"),
                 bg="#45475a", fg="#cdd6f4", relief=tk.FLAT).pack(pady=2, fill=tk.X)
        
        tk.Label(left_panel, text="📚 CROPS", font=("Arial", 10, "bold"), bg="#313244", fg="#89dceb").pack(pady=(10, 5))
        
        crop_frame = tk.Frame(left_panel, bg="#313244")
        crop_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        crop_scroll = tk.Scrollbar(crop_frame)
        crop_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.crop_listbox = tk.Listbox(crop_frame, bg="#45475a", fg="#cdd6f4", yscrollcommand=crop_scroll.set,
                                      font=("Arial", 7), relief=tk.FLAT, bd=0)
        self.crop_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        crop_scroll.config(command=self.crop_listbox.yview)
        
        for crop_name in CropData.CROPS.keys():
            self.crop_listbox.insert(tk.END, crop_name)
        self.crop_listbox.bind("<<ListboxSelect>>", self.on_crop_select)
        
        # CENTER - CANVAS
        self.canvas = tk.Canvas(main_frame, bg="#2d2d44", width=480, height=400, highlightthickness=0)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        
        # RIGHT PANEL
        right_panel = tk.Frame(main_frame, bg="#313244", width=180)
        right_panel.pack(side=tk.LEFT, fill=tk.Y, padx=5)
        right_panel.pack_propagate(False)
        
        tk.Label(right_panel, text="📊 STATUS", font=("Arial", 10, "bold"), bg="#313244", fg="#89dceb").pack(pady=5)
        
        self.status_text = tk.Label(right_panel, text="", font=("Arial", 8), bg="#313244", fg="#cdd6f4", justify=tk.LEFT)
        self.status_text.pack(padx=5, pady=5)
        
        tk.Label(right_panel, text="📋 ASSETS", font=("Arial", 10, "bold"), bg="#313244", fg="#89dceb").pack(pady=(10, 5))
        
        asset_frame = tk.Frame(right_panel, bg="#313244")
        asset_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        asset_scroll = tk.Scrollbar(asset_frame)
        asset_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.asset_listbox = tk.Listbox(asset_frame, bg="#45475a", fg="#cdd6f4", yscrollcommand=asset_scroll.set,
                                       font=("Arial", 7), relief=tk.FLAT, bd=0)
        self.asset_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        asset_scroll.config(command=self.asset_listbox.yview)
        
        # List available asset categories
        for category, assets in CropData.AVAILABLE_ASSETS.items():
            self.asset_listbox.insert(tk.END, f"[{category.upper()}] ({len(assets)} assets)")
            for asset in assets[:3]:
                self.asset_listbox.insert(tk.END, f"  {asset}")
            if len(assets) > 3:
                self.asset_listbox.insert(tk.END, f"  ... +{len(assets)-3} more")
        
        # BOTTOM
        bottom_frame = tk.Frame(self, bg="#313244", height=50)
        bottom_frame.pack(fill=tk.X, padx=5, pady=5)
        bottom_frame.pack_propagate(False)
        
        tk.Label(bottom_frame, text="⬅️ ⬆️ ⬇️ ➡️ MOVE | SPACE: INTERACT", font=("Arial", 9),
                bg="#313244", fg="#a6e3a1").pack(side=tk.LEFT, padx=10, pady=5)
        
        tk.Button(bottom_frame, text="🏪 Shop", font=("Arial", 9), command=self.show_shop,
                 bg="#45475a", fg="#cdd6f4", relief=tk.FLAT).pack(side=tk.RIGHT, padx=5, pady=5)
        tk.Button(bottom_frame, text="💤 Rest", font=("Arial", 9), command=self.perform_rest,
                 bg="#45475a", fg="#cdd6f4", relief=tk.FLAT).pack(side=tk.RIGHT, padx=5, pady=5)
        tk.Button(bottom_frame, text="💾 Save", font=("Arial", 9), command=self.save_game,
                 bg="#45475a", fg="#cdd6f4", relief=tk.FLAT).pack(side=tk.RIGHT, padx=5, pady=5)
        
        self.action_mode = None
    
    def bind_keys(self):
        """Bind keys"""
        self.parent.bind("<KeyPress>", self.on_key_press)
        self.parent.bind("<KeyRelease>", self.on_key_release)
    
    def on_key_press(self, event):
        """Handle key press"""
        self.keys_pressed.add(event.keysym)
        
        if event.keysym == "Left":
            self.state.move_player(-1, 0)
        elif event.keysym == "Right":
            self.state.move_player(1, 0)
        elif event.keysym == "Up":
            self.state.move_player(0, -1)
        elif event.keysym == "Down":
            self.state.move_player(0, 1)
        elif event.keysym == "space":
            self.interact_npc()
    
    def on_key_release(self, event):
        """Handle key release"""
        self.keys_pressed.discard(event.keysym)
    
    def on_canvas_click(self, event):
        """Handle canvas click"""
        if not self.action_mode:
            return
        
        x = event.x // self.cell_size
        y = event.y // self.cell_size
        
        viewport_x = self.state.player_x - self.viewport_width // 2
        viewport_y = self.state.player_y - self.viewport_height // 2
        
        world_x = viewport_x + x
        world_y = viewport_y + y
        
        if 0 <= world_x < 12 and 0 <= world_y < 12:
            self.perform_action(world_x, world_y)
    
    def on_crop_select(self, event):
        """Handle crop selection"""
        selection = self.crop_listbox.curselection()
        if selection:
            self.state.selected_crop = self.crop_listbox.get(selection[0])
    
    def perform_action(self, x, y):
        """Perform action on cell"""
        if not self.action_mode:
            return
        
        cell = self.state.farm.get((x, y), {})
        
        if self.action_mode == "plant":
            if not cell.get("plant") and self.state.selected_crop:
                crop_data = CropData.CROPS[self.state.selected_crop]
                if self.state.money >= crop_data["seed_cost"] and self.state.consume_energy(crop_data["energy_cost"]):
                    cell["plant"] = self.state.selected_crop
                    cell["growth"] = 0
                    self.state.money -= crop_data["seed_cost"]
                    self.action_mode = None
        
        elif self.action_mode == "water":
            if cell.get("plant"):
                cell["watered"] = True
                self.state.consume_energy(1)
                self.action_mode = None
        
        elif self.action_mode == "harvest":
            if cell.get("plant") and cell["growth"] >= 100:
                crop_name = cell["plant"]
                self.state.inventory[crop_name] = self.state.inventory.get(crop_name, 0) + 1
                self.state.money += CropData.CROPS[crop_name]["sell_price"]
                cell["plant"] = None
                cell["growth"] = 0
                self.state.consume_energy(2)
                self.action_mode = None
        
        elif self.action_mode == "clear":
            cell["plant"] = None
            cell["growth"] = 0
            self.state.consume_energy(1)
            self.action_mode = None
    
    def select_action(self, action):
        """Select action"""
        self.action_mode = action
        messagebox.showinfo("Action Selected", f"Click on a farm tile to {action}")
    
    def place_building(self, building_type):
        """Place building"""
        cost = self.state.get_building_cost(building_type)
        if self.state.money >= cost:
            self.action_mode = f"build_{building_type}"
            messagebox.showinfo("Building", f"Click to place {building_type} (${cost})")
        else:
            messagebox.showerror("Insufficient Funds", f"Need ${cost}, have ${self.state.money}")
    
    def interact_npc(self):
        """Interact with NPC"""
        for npc_name, npc_data in self.state.npcs.items():
            if npc_data["location"] == (self.state.player_x, self.state.player_y):
                messagebox.showinfo(npc_name, npc_data["dialogue"])
                self.state.relationships[npc_name] = self.state.relationships.get(npc_name, 0) + 1
                return
    
    def show_shop(self):
        """Show shop"""
        shop_window = tk.Toplevel(self.parent)
        shop_window.title("🏪 Shop - Buy Seeds")
        shop_window.geometry("400x500")
        shop_window.configure(bg="#1e1e2e")
        
        tk.Label(shop_window, text="🌱 SEEDS FOR SALE", font=("Arial", 12, "bold"),
                bg="#1e1e2e", fg="#89b4fa").pack(pady=5)
        
        for crop_name, crop_data in sorted(CropData.CROPS.items()):
            frame = tk.Frame(shop_window, bg="#313244")
            frame.pack(fill=tk.X, padx=10, pady=3)
            
            tk.Label(frame, text=f"{crop_name} - ${crop_data['seed_cost']}", font=("Arial", 10),
                    bg="#313244", fg="#cdd6f4").pack(side=tk.LEFT)
            tk.Button(frame, text="Buy", font=("Arial", 9),
                     command=lambda cn=crop_name, cost=crop_data['seed_cost']: self.buy_crop(cn, cost),
                     bg="#45475a", fg="#cdd6f4", relief=tk.FLAT, width=8).pack(side=tk.RIGHT)
    
    def buy_crop(self, crop_name, cost):
        """Buy crop"""
        if self.state.money >= cost:
            self.state.money -= cost
            self.state.inventory[crop_name] = self.state.inventory.get(crop_name, 0) + 1
            messagebox.showinfo("Purchase", f"Bought {crop_name}!")
            self.update_display()
        else:
            messagebox.showerror("Insufficient Funds", f"Need ${cost}, have ${self.state.money}")
    
    def perform_rest(self):
        """Rest"""
        self.state.rest()
        self.state.update_temperature()
        self.state.check_special_events()
        self.state.new_day()
        self.update_display()
    
    def update_game_loop(self):
        """Game loop"""
        self.update_display()
        self.after(100, self.update_game_loop)
    
    def draw_viewport(self):
        """Draw viewport"""
        self.canvas.delete("all")
        
        viewport_x = self.state.player_x - self.viewport_width // 2
        viewport_y = self.state.player_y - self.viewport_height // 2
        
        # Draw background
        self.canvas.create_rectangle(0, 0, self.canvas.winfo_width(), self.canvas.winfo_height(),
                                    fill="#2d2d44", outline="")
        
        # Draw grid
        for screen_x in range(self.viewport_width):
            for screen_y in range(self.viewport_height):
                world_x = viewport_x + screen_x
                world_y = viewport_y + screen_y
                
                if 0 <= world_x < 12 and 0 <= world_y < 12:
                    x1 = screen_x * self.cell_size
                    y1 = screen_y * self.cell_size
                    x2 = x1 + self.cell_size
                    y2 = y1 + self.cell_size
                    
                    # Cell background with subtle gradient effect
                    self.canvas.create_rectangle(x1, y1, x2, y2, fill="#313244", outline="#45475a")
                    
                    cell = self.state.farm[(world_x, world_y)]
                    
                    # Draw plant
                    if cell["plant"]:
                        growth = cell["growth"]
                        if growth < 25:
                            emoji = "•"
                        elif growth < 50:
                            emoji = "🌱"
                        elif growth < 75:
                            emoji = "🌿"
                        else:
                            emoji = CropData.CROPS[cell["plant"]]["emoji"]
                        
                        self.canvas.create_text(x1 + self.cell_size // 2, y1 + self.cell_size // 2,
                                              text=emoji, font=("Arial", 24))
                    
                    # Draw building
                    if (world_x, world_y) in self.state.buildings:
                        building_type = self.state.buildings[(world_x, world_y)]["type"]
                        building_emoji = {"fence": "🚧", "chest": "📦", "shed": "🏠", "greenhouse": "🌿"}
                        emoji = building_emoji.get(building_type, "📦")
                        self.canvas.create_text(x1 + self.cell_size // 2, y1 + self.cell_size // 2,
                                              text=emoji, font=("Arial", 20))
                    
                    # Draw NPC
                    for npc_name, npc_data in self.state.npcs.items():
                        if npc_data["location"] == (world_x, world_y):
                            self.canvas.create_text(x1 + self.cell_size // 2, y1 + self.cell_size // 2,
                                                  text="👤", font=("Arial", 22))
        
        # Draw player
        center_x = (self.viewport_width // 2) * self.cell_size + self.cell_size // 2
        center_y = (self.viewport_height // 2) * self.cell_size + self.cell_size // 2
        self.canvas.create_text(center_x, center_y, text="🧑", font=("Arial", 26))
    
    def update_display(self):
        """Update display"""
        self.state.update_temperature()
        
        self.day_label.config(text=f"📅 Day {self.state.day}")
        self.season_label.config(text=f"🍂 {self.state.get_season()}")
        self.temp_label.config(text=f"🌡️ {self.state.temperature}°F")
        self.money_label.config(text=f"💰 ${self.state.money}")
        self.energy_label.config(text=f"⚡ {self.state.energy}/{self.state.max_energy}")
        
        status = f"Position: ({self.state.player_x}, {self.state.player_y})\n"
        status += f"Mode: {self.action_mode or 'Normal'}\n"
        if self.state.selected_crop:
            crop_short = self.state.selected_crop.split()[1] if " " in self.state.selected_crop else "?"
            status += f"Crop: {crop_short}"
        self.status_text.config(text=status)
        
        self.draw_viewport()
    
    def save_game(self):
        """Save game"""
        save_data = {
            "money": self.state.money,
            "day": self.state.day,
            "energy": self.state.energy,
            "player_x": self.state.player_x,
            "player_y": self.state.player_y,
            "inventory": self.state.inventory,
            "farm": {str(k): v for k, v in self.state.farm.items()},
            "buildings": {str(k): v for k, v in self.state.buildings.items()}
        }
        
        with open("croptopia_save.json", "w") as f:
            json.dump(save_data, f, indent=2)
        
        messagebox.showinfo("Saved", "Game saved to croptopia_save.json")


def launch_croptopia():
    """Launch game"""
    root = tk.Tk()
    root.title("🌾 Ultimate Croptopia v3.5 - Asset Enhanced")
    root.geometry("1400x700")
    root.configure(bg="#1e1e2e")
    
    game = UltimatecroptopiaGame(root)
    game.pack(fill=tk.BOTH, expand=True)
    
    root.mainloop()


if __name__ == "__main__":
    launch_croptopia()
