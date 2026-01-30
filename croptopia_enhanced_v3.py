"""
DoubOS - Ultimate Croptopia v3.0 - Enhanced with Player Movement & Viewport
Features: 12x12 farm grid, 10 crops, hotbar, shop, crafting, day/night cycle, save system
Enhanced: Player character movement, viewport rendering, immersive gameplay
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import json
import os
import math


class CropData:
    """Defines crop characteristics"""
    CROPS = {
        "🌿 Chives": {
            "seed_cost": 20,
            "sell_price": 35,
            "growth_days": 5,
            "energy_cost": 3,
            "emoji": "🌿",
            "color": "#8bc34a"
        },
        "🌾 Wheat": {
            "seed_cost": 5,
            "sell_price": 12,
            "growth_days": 2,
            "energy_cost": 1,
            "emoji": "🌾",
            "color": "#cddc39"
        },
        "🥕 Carrot": {
            "seed_cost": 10,
            "sell_price": 18,
            "growth_days": 3,
            "energy_cost": 1,
            "emoji": "🥕",
            "color": "#ff9800"
        },
        "🥔 Potato": {
            "seed_cost": 12,
            "sell_price": 20,
            "growth_days": 3,
            "energy_cost": 2,
            "emoji": "🥔",
            "color": "#a1887f"
        },
        "🍎 Apple": {
            "seed_cost": 15,
            "sell_price": 25,
            "growth_days": 4,
            "energy_cost": 2,
            "emoji": "🍎",
            "color": "#f44336"
        },
        "🍀 Sorrel": {
            "seed_cost": 25,
            "sell_price": 42,
            "growth_days": 6,
            "energy_cost": 3,
            "emoji": "🍀",
            "color": "#4caf50"
        },
        "🍓 Cranberry": {
            "seed_cost": 30,
            "sell_price": 55,
            "growth_days": 7,
            "energy_cost": 4,
            "emoji": "🍓",
            "color": "#e91e63"
        },
        "🫐 Elderberry": {
            "seed_cost": 28,
            "sell_price": 50,
            "growth_days": 6,
            "energy_cost": 3,
            "emoji": "🫐",
            "color": "#673ab7"
        },
        "❤️ Redbaneberry": {
            "seed_cost": 22,
            "sell_price": 40,
            "growth_days": 5,
            "energy_cost": 3,
            "emoji": "❤️",
            "color": "#c2185b"
        },
        "🌰 Apricorn": {
            "seed_cost": 18,
            "sell_price": 32,
            "growth_days": 4,
            "energy_cost": 2,
            "emoji": "🌰",
            "color": "#ff6f00"
        }
    }


class GameState:
    """Manage all game state"""
    
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
        
        # PLAYER POSITION (NEW)
        self.player_x = 6
        self.player_y = 6
        
        # Initialize hotbar (8 slots)
        for i in range(1, 9):
            self.hotbar[i] = None
            
        # Initialize inventory
        for crop_name in CropData.CROPS:
            self.inventory[crop_name] = 0
        self.inventory["Stick"] = 5
        self.inventory["Flint"] = 3
        self.inventory["Wood"] = 0
        self.inventory["Stone"] = 0
        
        # Initialize farm grid (12x12)
        for x in range(12):
            for y in range(12):
                self.farm[(x, y)] = {
                    "plant": None,
                    "growth": 0,
                    "watered": False,
                    "age": 0,
                    "quality": 1.0
                }
        
        # Initialize NPCs
        self.init_npcs()
        self.check_special_events()
    
    def move_player(self, dx, dy):
        """Move player with boundary checking"""
        new_x = max(0, min(11, self.player_x + dx))
        new_y = max(0, min(11, self.player_y + dy))
        
        if (new_x, new_y) != (self.player_x, self.player_y):
            self.player_x = new_x
            self.player_y = new_y
            return True
        return False
    
    def get_season(self):
        """Calculate current season based on day"""
        cycle = (self.day - 1) // 28
        season_index = cycle % 4
        seasons = ["Spring", "Summer", "Fall", "Winter"]
        return seasons[season_index]
    
    def update_temperature(self):
        """Update temperature based on season"""
        season = self.get_season()
        season_temps = {
            "Spring": 65,
            "Summer": 85,
            "Fall": 60,
            "Winter": 35
        }
        import random
        self.temperature = season_temps.get(season, 70) + random.randint(-10, 10)
    
    def init_npcs(self):
        """Initialize NPCs with schedules"""
        self.npcs = {
            "Mayor": {"location": (5, 2), "dialogue": "The crops look healthy!", "schedule": "morning", "relationship": 0},
            "Merchant": {"location": (3, 4), "dialogue": "Welcome to my shop!", "schedule": "always", "relationship": 0},
            "Farmer": {"location": (8, 8), "dialogue": "Been farming for 20 years.", "schedule": "afternoon", "relationship": 0},
            "Guard": {"location": (10, 1), "dialogue": "Keeping watch for trouble.", "schedule": "always", "relationship": 0}
        }
    
    def check_special_events(self):
        """Check for special events"""
        if self.day % 20 == 0 and self.day > 0:
            self.events.append({"type": "raid", "name": "Lunar Crusader Raid", "day": self.day, "reward": 100})
        if self.day % 28 == 0 and self.day > 0:
            self.events.append({"type": "speech", "name": "Mayor's Speech", "day": self.day, "text": "The community is thriving!"})
    
    def add_building(self, x, y, building_type):
        """Add construction structure"""
        if (x, y) not in self.buildings:
            self.buildings[(x, y)] = {"type": building_type, "built_day": self.day, "condition": 100}
            return True
        return False
    
    def get_building_cost(self, building_type):
        """Get cost to build"""
        costs = {"fence": 50, "chest": 75, "shed": 200, "greenhouse": 400}
        return costs.get(building_type, 100)
    
    def consume_energy(self, amount):
        """Use energy"""
        self.energy = max(0, self.energy - amount)
        return self.energy > 0
    
    def rest(self):
        """Restore energy"""
        self.energy = min(self.max_energy, self.energy + 30)
        self.day += 1
    
    def new_day(self):
        """Advance to next day"""
        self.day += 1
        self.season = self.get_season()
        for pos, cell in self.farm.items():
            if cell["plant"] and cell["growth"] < 100:
                cell["growth"] = min(100, cell["growth"] + 20)
            if cell["watered"]:
                cell["watered"] = False


class UltimatecroptopiaGame(tk.Frame):
    """Ultimate Croptopia v3.0 with Viewport System"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.parent = parent
        self.state = GameState()
        self.cell_size = 40  # Larger cells for better visibility
        self.viewport_width = 12  # Cells visible
        self.viewport_height = 10
        
        # Movement tracking
        self.keys_pressed = set()
        
        self.setup_ui()
        self.bind_keys()
        self.update_game_loop()
        self.update_display()
        
    def setup_ui(self):
        """Create all UI elements"""
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
        
        # MAIN GAME AREA
        main_frame = tk.Frame(self, bg="#1e1e2e")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Left panel - Tools
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
        
        # CENTER - CANVAS (Viewport)
        self.canvas = tk.Canvas(main_frame, bg="#2d2d44", width=480, height=400, highlightthickness=0)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        
        # RIGHT PANEL - Info
        right_panel = tk.Frame(main_frame, bg="#313244", width=180)
        right_panel.pack(side=tk.LEFT, fill=tk.Y, padx=5)
        right_panel.pack_propagate(False)
        
        tk.Label(right_panel, text="📊 STATUS", font=("Arial", 10, "bold"), bg="#313244", fg="#89dceb").pack(pady=5)
        
        self.status_text = tk.Label(right_panel, text="", font=("Arial", 8), bg="#313244", fg="#cdd6f4", justify=tk.LEFT)
        self.status_text.pack(padx=5, pady=5)
        
        tk.Label(right_panel, text="📚 INVENTORY", font=("Arial", 10, "bold"), bg="#313244", fg="#89dceb").pack(pady=(10, 5))
        
        inv_frame = tk.Frame(right_panel, bg="#313244")
        inv_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        inv_scroll = tk.Scrollbar(inv_frame)
        inv_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.inventory_listbox = tk.Listbox(inv_frame, bg="#45475a", fg="#cdd6f4", yscrollcommand=inv_scroll.set, 
                                           font=("Arial", 8), relief=tk.FLAT, bd=0)
        self.inventory_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        inv_scroll.config(command=self.inventory_listbox.yview)
        
        # BOTTOM - Control buttons
        bottom_frame = tk.Frame(self, bg="#313244", height=50)
        bottom_frame.pack(fill=tk.X, padx=5, pady=5)
        bottom_frame.pack_propagate(False)
        
        tk.Label(bottom_frame, text="⬅️ ⬆️ ⬇️ ➡️ to move | SPACE to interact", font=("Arial", 9),
                bg="#313244", fg="#a6e3a1").pack(side=tk.LEFT, padx=10, pady=5)
        
        tk.Button(bottom_frame, text="🏪 Shop", font=("Arial", 9), command=self.show_shop,
                 bg="#45475a", fg="#cdd6f4", relief=tk.FLAT).pack(side=tk.RIGHT, padx=5, pady=5)
        tk.Button(bottom_frame, text="💤 Rest", font=("Arial", 9), command=self.perform_rest,
                 bg="#45475a", fg="#cdd6f4", relief=tk.FLAT).pack(side=tk.RIGHT, padx=5, pady=5)
        tk.Button(bottom_frame, text="💾 Save", font=("Arial", 9), command=self.save_game,
                 bg="#45475a", fg="#cdd6f4", relief=tk.FLAT).pack(side=tk.RIGHT, padx=5, pady=5)
        
        self.action_mode = None
        
    def bind_keys(self):
        """Bind keyboard controls"""
        self.parent.bind("<KeyPress>", self.on_key_press)
        self.parent.bind("<KeyRelease>", self.on_key_release)
        
    def on_key_press(self, event):
        """Handle key press"""
        self.keys_pressed.add(event.keysym)
        
        # Direct movement
        if event.keysym == "Left":
            self.state.move_player(-1, 0)
        elif event.keysym == "Right":
            self.state.move_player(1, 0)
        elif event.keysym == "Up":
            self.state.move_player(0, -1)
        elif event.keysym == "Down":
            self.state.move_player(0, 1)
        elif event.keysym == "space":
            # Interact with what's in front of player
            self.interact_npc()
        
    def on_key_release(self, event):
        """Handle key release"""
        self.keys_pressed.discard(event.keysym)
    
    def on_canvas_click(self, event):
        """Handle canvas click to perform action on grid"""
        if not self.action_mode:
            return
        
        # Calculate grid position from canvas click
        x = event.x // self.cell_size
        y = event.y // self.cell_size
        
        # Convert to world coordinates
        viewport_x = self.state.player_x - self.viewport_width // 2
        viewport_y = self.state.player_y - self.viewport_height // 2
        
        world_x = viewport_x + x
        world_y = viewport_y + y
        
        # Clamp to farm boundaries
        if 0 <= world_x < 12 and 0 <= world_y < 12:
            self.perform_action(world_x, world_y)
    
    def perform_action(self, x, y):
        """Perform action on grid cell"""
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
        """Select tool action"""
        self.action_mode = action
        messagebox.showinfo("Action Selected", f"Click on a farm tile to {action}")
    
    def place_building(self, building_type):
        """Place a building"""
        cost = self.state.get_building_cost(building_type)
        if self.state.money >= cost:
            self.action_mode = f"build_{building_type}"
            messagebox.showinfo("Building", f"Click to place {building_type} (${cost})")
        else:
            messagebox.showerror("Insufficient Funds", f"Need ${cost}, have ${self.state.money}")
    
    def interact_npc(self):
        """Interact with NPC at player location"""
        for npc_name, npc_data in self.state.npcs.items():
            if npc_data["location"] == (self.state.player_x, self.state.player_y):
                messagebox.showinfo(npc_name, npc_data["dialogue"])
                self.state.relationships[npc_name] = self.state.relationships.get(npc_name, 0) + 1
                return
    
    def show_shop(self):
        """Show shop interface"""
        shop_window = tk.Toplevel(self.parent)
        shop_window.title("🏪 Shop")
        shop_window.geometry("400x400")
        shop_window.configure(bg="#1e1e2e")
        
        tk.Label(shop_window, text="🌱 SEEDS", font=("Arial", 12, "bold"), bg="#1e1e2e", fg="#89b4fa").pack(pady=5)
        
        for crop_name, crop_data in CropData.CROPS.items():
            frame = tk.Frame(shop_window, bg="#313244")
            frame.pack(fill=tk.X, padx=10, pady=5)
            
            tk.Label(frame, text=f"{crop_name} - ${crop_data['seed_cost']}", font=("Arial", 10),
                    bg="#313244", fg="#cdd6f4").pack(side=tk.LEFT)
            tk.Button(frame, text="Buy", font=("Arial", 9), 
                     command=lambda cn=crop_name, cost=crop_data['seed_cost']: self.buy_crop(cn, cost),
                     bg="#45475a", fg="#cdd6f4", relief=tk.FLAT).pack(side=tk.RIGHT)
    
    def buy_crop(self, crop_name, cost):
        """Buy crop from shop"""
        if self.state.money >= cost:
            self.state.money -= cost
            self.state.inventory[crop_name] = self.state.inventory.get(crop_name, 0) + 1
            messagebox.showinfo("Purchase", f"Bought {crop_name}!")
            self.update_display()
        else:
            messagebox.showerror("Insufficient Funds", f"Need ${cost}, have ${self.state.money}")
    
    def perform_rest(self):
        """Rest and advance day"""
        self.state.rest()
        self.state.update_temperature()
        self.state.check_special_events()
        self.state.new_day()
        self.update_display()
    
    def update_game_loop(self):
        """Game loop for movement and rendering"""
        self.update_display()
        self.after(100, self.update_game_loop)
    
    def draw_viewport(self):
        """Draw viewport centered on player"""
        self.canvas.delete("all")
        
        # Calculate viewport boundaries
        viewport_x = self.state.player_x - self.viewport_width // 2
        viewport_y = self.state.player_y - self.viewport_height // 2
        
        # Draw background gradient
        self.canvas.create_rectangle(0, 0, self.canvas.winfo_width(), self.canvas.winfo_height(),
                                    fill="#2d2d44", outline="")
        
        # Draw grid
        for screen_x in range(self.viewport_width):
            for screen_y in range(self.viewport_height):
                world_x = viewport_x + screen_x
                world_y = viewport_y + screen_y
                
                if 0 <= world_x < 12 and 0 <= world_y < 12:
                    # Draw cell background
                    x1 = screen_x * self.cell_size
                    y1 = screen_y * self.cell_size
                    x2 = x1 + self.cell_size
                    y2 = y1 + self.cell_size
                    
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
        
        # Draw player in center
        center_x = (self.viewport_width // 2) * self.cell_size + self.cell_size // 2
        center_y = (self.viewport_height // 2) * self.cell_size + self.cell_size // 2
        self.canvas.create_text(center_x, center_y, text="🧑", font=("Arial", 26))
    
    def update_display(self):
        """Update all UI elements"""
        self.state.update_temperature()
        
        # Update top bar
        self.day_label.config(text=f"📅 Day {self.state.day}")
        self.season_label.config(text=f"🍂 {self.state.get_season()}")
        self.temp_label.config(text=f"🌡️ {self.state.temperature}°F")
        self.money_label.config(text=f"💰 ${self.state.money}")
        self.energy_label.config(text=f"⚡ {self.state.energy}/{self.state.max_energy}")
        
        # Update status
        status = f"Position: ({self.state.player_x}, {self.state.player_y})\n"
        status += f"Mode: {self.action_mode or 'Normal'}\n"
        if self.state.selected_crop:
            status += f"Selected: {self.state.selected_crop}"
        self.status_text.config(text=status)
        
        # Update inventory
        self.inventory_listbox.delete(0, tk.END)
        for item, count in sorted(self.state.inventory.items()):
            if count > 0:
                self.inventory_listbox.insert(tk.END, f"{item}: {count}")
        
        # Draw viewport
        self.draw_viewport()
    
    def save_game(self):
        """Save game state"""
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
        
        save_path = "croptopia_save.json"
        with open(save_path, "w") as f:
            json.dump(save_data, f, indent=2)
        
        messagebox.showinfo("Saved", f"Game saved to {save_path}")


def launch_croptopia():
    """Launch game window"""
    root = tk.Tk()
    root.title("🌾 Ultimate Croptopia v3.0")
    root.geometry("1400x700")
    root.configure(bg="#1e1e2e")
    
    game = UltimatecroptopiaGame(root)
    game.pack(fill=tk.BOTH, expand=True)
    
    root.mainloop()


if __name__ == "__main__":
    launch_croptopia()
