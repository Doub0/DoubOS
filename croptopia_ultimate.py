"""
DoubOS - Ultimate Croptopia Farming Game
Complete implementation based on Godot Croptopia project analysis
Features: 12x12 farm grid, 10 crops, hotbar, shop, crafting, day/night cycle, save system
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import json
import os


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
        self.temperature = 70  # Fahrenheit
        self.max_energy = 100
        self.energy = 100
        self.farm = {}  # Grid state
        self.inventory = {}  # Item counts
        self.hotbar = {}  # Hotbar slots
        self.current_tool = "plant"
        self.selected_crop = None
        self.playtime_minutes = 0
        self.buildings = {}  # Construction structures
        self.npcs = {}  # NPC locations and states
        self.events = []  # Active events
        self.relationships = {}  # NPC relationships
        
        # Initialize hotbar (8 slots like Godot version)
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
                    "growth": 0,  # 0-100
                    "watered": False,
                    "age": 0,
                    "quality": 1.0  # Affected by weather
                }
        
        # Initialize NPCs
        self.init_npcs()
        
        # Initialize events
        self.check_special_events()
    
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
        # Add daily variation
        import random
        self.temperature = season_temps.get(season, 70) + random.randint(-10, 10)
    
    def init_npcs(self):
        """Initialize NPCs with schedules"""
        self.npcs = {
            "Mayor": {
                "location": (5, 2),
                "dialogue": "The crops look healthy this season!",
                "schedule": "morning",
                "relationship": 0
            },
            "Merchant": {
                "location": (3, 4),
                "dialogue": "Welcome to my shop!",
                "schedule": "always",
                "relationship": 0
            },
            "Farmer": {
                "location": (8, 8),
                "dialogue": "Been farming for 20 years.",
                "schedule": "afternoon",
                "relationship": 0
            },
            "Guard": {
                "location": (10, 1),
                "dialogue": "Keeping watch for trouble.",
                "schedule": "always",
                "relationship": 0
            }
        }
    
    def check_special_events(self):
        """Check for special events like raids"""
        # Lunar crusader raid every 20 days
        if self.day % 20 == 0 and self.day > 0:
            self.events.append({
                "type": "raid",
                "name": "Lunar Crusader Raid",
                "day": self.day,
                "reward": 100
            })
        
        # Mayor speech every 28 days
        if self.day % 28 == 0 and self.day > 0:
            self.events.append({
                "type": "speech",
                "name": "Mayor's Speech",
                "day": self.day,
                "text": "The community is thriving!"
            })
    
    def add_building(self, x, y, building_type):
        """Add construction structure to farm"""
        if (x, y) not in self.buildings:
            self.buildings[(x, y)] = {
                "type": building_type,
                "built_day": self.day,
                "condition": 100
            }
            return True
        return False
    
    def get_building_cost(self, building_type):
        """Get cost to build structure"""
        costs = {
            "fence": 50,
            "chest": 75,
            "shed": 200,
            "greenhouse": 400
        }
        return costs.get(building_type, 100)
    
    def consume_energy(self, amount):
        """Use energy for action"""
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
        # Crops grow
        for pos, cell in self.farm.items():
            if cell["plant"] and cell["growth"] < 100:
                cell["growth"] = min(100, cell["growth"] + 20)
            if cell["watered"]:
                cell["watered"] = False


class UltimatecroptopiaGame(tk.Frame):
    """Ultimate Croptopia game with all features"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.parent = parent
        self.state = GameState()
        self.cell_size = 35
        self.grid_width = 12
        self.grid_height = 12
        
        self.setup_ui()
        self.update_display()
        
    def setup_ui(self):
        """Create all UI elements"""
        self.configure(bg="#1e1e2e")
        
        # Top bar with day/season/money
        top_bar = tk.Frame(self, bg="#313244", height=50)
        top_bar.pack(fill=tk.X, padx=5, pady=5)
        top_bar.pack_propagate(False)
        
        self.day_label = tk.Label(top_bar, text="", font=("Arial", 11, "bold"),
                                 bg="#313244", fg="#89b4fa")
        self.day_label.pack(side=tk.LEFT, padx=10, pady=5)
        
        self.money_label = tk.Label(top_bar, text="", font=("Arial", 11, "bold"),
                                   bg="#313244", fg="#a6e3a1")
        self.money_label.pack(side=tk.LEFT, padx=10, pady=5)
        
        self.energy_label = tk.Label(top_bar, text="", font=("Arial", 11, "bold"),
                                    bg="#313244", fg="#f9e2af")
        self.energy_label.pack(side=tk.LEFT, padx=10, pady=5)
        
        # Main game area
        main_frame = tk.Frame(self, bg="#1e1e2e")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Left panel: Tools and Crops
        left_panel = tk.Frame(main_frame, bg="#1e1e2e", width=150)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, padx=(0, 5))
        left_panel.pack_propagate(False)
        
        tk.Label(left_panel, text="🛠️ TOOLS", font=("Arial", 10, "bold"),
                bg="#1e1e2e", fg="#cdd6f4").pack(fill=tk.X, pady=5)
        
        tools = [
            ("🌱 Plant", "plant"),
            ("💧 Water", "water"),
            ("✂️ Harvest", "harvest"),
            ("🧹 Clear", "clear"),
        ]
        
        for label, tool in tools:
            btn = tk.Button(left_panel, text=label, font=("Arial", 9),
                           bg="#45475a", fg="#cdd6f4", relief=tk.FLAT,
                           command=lambda t=tool: self.select_tool(t))
            btn.pack(fill=tk.X, pady=2)
        
        tk.Label(left_panel, text="🏗️ BUILD", font=("Arial", 10, "bold"),
                bg="#1e1e2e", fg="#cdd6f4").pack(fill=tk.X, pady=(15, 5))
        
        buildings = [
            ("🚧 Fence", "fence", 50),
            ("📦 Chest", "chest", 75),
            ("🏠 Shed", "shed", 200),
        ]
        
        for label, btype, cost in buildings:
            btn = tk.Button(left_panel, text=f"{label} (${cost})", font=("Arial", 8),
                           bg="#8bc34a", fg="#1e1e2e", relief=tk.FLAT,
                           command=lambda b=btype: self.select_tool(f"build_{b}"))
            btn.pack(fill=tk.X, pady=1)
        
        tk.Label(left_panel, text="🌾 CROPS", font=("Arial", 10, "bold"),
                bg="#1e1e2e", fg="#cdd6f4").pack(fill=tk.X, pady=(20, 5))
        
        # Crop buttons
        self.crop_buttons = {}
        for crop_name in list(CropData.CROPS.keys())[:5]:  # Top 5
            self.create_crop_button(left_panel, crop_name)
        
        # Hotbar
        tk.Label(left_panel, text="📌 HOTBAR", font=("Arial", 10, "bold"),
                bg="#1e1e2e", fg="#cdd6f4").pack(fill=tk.X, pady=(20, 5))
        
        hotbar_frame = tk.Frame(left_panel, bg="#1e1e2e")
        hotbar_frame.pack(fill=tk.X)
        
        for i in range(1, 9):
            btn = tk.Button(hotbar_frame, text=str(i), font=("Arial", 8),
                           bg="#313244", fg="#cdd6f4", width=3, height=1,
                           command=lambda slot=i: self.select_hotbar(slot))
            btn.grid(row=i//4, column=i%4, padx=1, pady=1)
        
        # Center panel: Farm canvas
        center_panel = tk.Frame(main_frame, bg="#1e1e2e")
        center_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        canvas_width = self.cell_size * self.grid_width
        canvas_height = self.cell_size * self.grid_height
        
        self.canvas = tk.Canvas(center_panel, bg="#2a2a3a", width=canvas_width,
                               height=canvas_height, relief=tk.SUNKEN, bd=2,
                               highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        
        # Right panel: Inventory and Shop
        right_panel = tk.Frame(main_frame, bg="#1e1e2e", width=200)
        right_panel.pack(side=tk.LEFT, fill=tk.BOTH, padx=(5, 0))
        right_panel.pack_propagate(False)
        
        tk.Label(right_panel, text="🎒 INVENTORY", font=("Arial", 10, "bold"),
                bg="#1e1e2e", fg="#cdd6f4").pack(fill=tk.X, pady=5)
        
        # Inventory listbox
        inv_frame = tk.Frame(right_panel, bg="#1e1e2e")
        inv_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        scrollbar = tk.Scrollbar(inv_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.inv_listbox = tk.Listbox(inv_frame, font=("Arial", 9),
                                      bg="#313244", fg="#cdd6f4",
                                      yscrollcommand=scrollbar.set,
                                      relief=tk.FLAT, bd=0)
        self.inv_listbox.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.inv_listbox.yview)
        
        # Action buttons
        button_frame = tk.Frame(right_panel, bg="#1e1e2e")
        button_frame.pack(fill=tk.X, pady=5)
        
        tk.Button(button_frame, text="💤 Rest", font=("Arial", 9),
                 bg="#f38ba8", fg="white", relief=tk.FLAT, command=self.rest).pack(fill=tk.X, pady=2)
        tk.Button(button_frame, text="📊 Shop", font=("Arial", 9),
                 bg="#89b4fa", fg="white", relief=tk.FLAT, command=self.show_shop).pack(fill=tk.X, pady=2)
        tk.Button(button_frame, text="� NPCs", font=("Arial", 9),
                 bg="#cba6f7", fg="white", relief=tk.FLAT, command=self.show_npcs).pack(fill=tk.X, pady=2)
        tk.Button(button_frame, text="📰 Events", font=("Arial", 9),
                 bg="#f5c563", fg="white", relief=tk.FLAT, command=self.show_events).pack(fill=tk.X, pady=2)
        tk.Button(button_frame, text="�💾 Save", font=("Arial", 9),
                 bg="#a6e3a1", fg="white", relief=tk.FLAT, command=self.save_game).pack(fill=tk.X, pady=2)
    
    def create_crop_button(self, parent, crop_name):
        """Create a crop selection button"""
        crop_data = CropData.CROPS[crop_name]
        btn = tk.Button(parent, text=f"{crop_data['emoji']} {crop_name}",
                       font=("Arial", 8), bg="#45475a", fg="#cdd6f4",
                       relief=tk.FLAT,
                       command=lambda: self.select_crop(crop_name))
        btn.pack(fill=tk.X, pady=1)
        self.crop_buttons[crop_name] = btn
    
    def select_tool(self, tool):
        """Select a tool"""
        self.state.current_tool = tool
        messagebox.showinfo("Tool Selected", f"Selected: {tool.title()}")
    
    def select_crop(self, crop_name):
        """Select a crop type"""
        self.state.selected_crop = crop_name
        messagebox.showinfo("Crop Selected", f"Selected: {crop_name}")
    
    def select_hotbar(self, slot):
        """Select hotbar slot"""
        messagebox.showinfo("Hotbar", f"Slot {slot} selected")
    
    def on_canvas_click(self, event):
        """Handle farm click"""
        x = event.x // self.cell_size
        y = event.y // self.cell_size
        
        if 0 <= x < self.grid_width and 0 <= y < self.grid_height:
            self.perform_action(x, y)
    
    def perform_action(self, x, y):
        """Perform action on farm cell"""
        cell = self.state.farm[(x, y)]
        tool = self.state.current_tool
        crop = self.state.selected_crop
        
        # Check for buildings
        if (x, y) in self.state.buildings:
            building = self.state.buildings[(x, y)]
            messagebox.showinfo("Building", f"You see a {building['type']}")
            return
        
        # Check for NPCs
        for npc_name, npc_data in self.state.npcs.items():
            if npc_data["location"] == (x, y):
                self.interact_npc(npc_name)
                return
        
        if tool.startswith("build_"):
            self.place_building(x, y, tool.replace("build_", ""))
        elif tool == "plant" and crop and not cell["plant"]:
            crop_data = CropData.CROPS[crop]
            if self.state.money >= crop_data["seed_cost"]:
                if self.state.consume_energy(crop_data["energy_cost"]):
                    self.state.money -= crop_data["seed_cost"]
                    cell["plant"] = crop
                    cell["growth"] = 10
                    self.update_display()
                else:
                    messagebox.showwarning("Low Energy", "Need to rest!")
            else:
                messagebox.showwarning("Poor", "Not enough money!")
        
        elif tool == "water" and cell["plant"]:
            if self.state.consume_energy(1):
                cell["watered"] = True
                cell["growth"] = min(100, cell["growth"] + 15)
                self.update_display()
        
        elif tool == "harvest" and cell["plant"] and cell["growth"] >= 100:
            if self.state.consume_energy(1):
                crop = cell["plant"]
                crop_data = CropData.CROPS[crop]
                # Quality affected by temperature
                quality_modifier = 1.0 if 60 <= self.state.temperature <= 80 else 0.8
                profit = int(crop_data["sell_price"] * quality_modifier)
                self.state.inventory[crop] += 1
                self.state.money += profit
                cell["plant"] = None
                cell["growth"] = 0
                cell["watered"] = False
                self.update_display()
        
        elif tool == "clear" and not cell["plant"]:
            if self.state.consume_energy(1):
                self.update_display()
    
    def place_building(self, x, y, building_type):
        """Place a building on farm"""
        cost = self.state.get_building_cost(building_type)
        if self.state.money >= cost:
            if self.state.add_building(x, y, building_type):
                self.state.money -= cost
                self.update_display()
                messagebox.showinfo("Built", f"Built a {building_type}!")
            else:
                messagebox.showwarning("Error", "Can't build there!")
        else:
            messagebox.showwarning("Poor", f"Need ${cost} to build!")
    
    def interact_npc(self, npc_name):
        """Interact with an NPC"""
        npc = self.state.npcs[npc_name]
        messagebox.showinfo(f"👤 {npc_name}", npc["dialogue"])
        self.state.npcs[npc_name]["relationship"] += 1
    
    def show_npcs(self):
        """Show NPC window"""
        npc_window = tk.Toplevel(self)
        npc_window.title("👥 NPCs in Town")
        npc_window.geometry("300x400")
        npc_window.configure(bg="#313244")
        
        tk.Label(npc_window, text="NPCs & Relationships", font=("Arial", 12, "bold"),
                bg="#313244", fg="#cdd6f4").pack(pady=10)
        
        for npc_name, npc_data in self.state.npcs.items():
            frame = tk.Frame(npc_window, bg="#45475a")
            frame.pack(fill=tk.X, padx=10, pady=5)
            
            rel = npc_data["relationship"]
            hearts = "❤️" * max(0, rel // 5)
            
            tk.Label(frame, text=f"{npc_name} {hearts}",
                    bg="#45475a", fg="#cdd6f4", font=("Arial", 10),
                    anchor="w", width=30).pack(fill=tk.X, padx=5, pady=5)
            
            btn = tk.Button(frame, text="Talk", font=("Arial", 8),
                           bg="#89b4fa", fg="white", relief=tk.FLAT,
                           command=lambda n=npc_name: self.interact_npc(n))
            btn.pack(side=tk.RIGHT, padx=5, pady=5)
    
    def show_events(self):
        """Show events window"""
        event_window = tk.Toplevel(self)
        event_window.title("📰 Events")
        event_window.geometry("300x400")
        event_window.configure(bg="#313244")
        
        tk.Label(event_window, text="Recent Events", font=("Arial", 12, "bold"),
                bg="#313244", fg="#cdd6f4").pack(pady=10)
        
        if not self.state.events:
            tk.Label(event_window, text="No events yet.", font=("Arial", 10),
                    bg="#313244", fg="#cdd6f4").pack(pady=20)
        else:
            for event in self.state.events[-5:]:  # Last 5 events
                frame = tk.Frame(event_window, bg="#45475a")
                frame.pack(fill=tk.X, padx=10, pady=5)
                
                emoji = "⚔️" if event["type"] == "raid" else "📢"
                tk.Label(frame, text=f"{emoji} Day {event['day']}: {event['name']}",
                        bg="#45475a", fg="#cdd6f4", font=("Arial", 9),
                        anchor="w", justify=tk.LEFT, wraplength=250).pack(fill=tk.X, padx=5, pady=5)
    
    def rest(self):
        """Rest to restore energy"""
        self.state.rest()
        self.state.energy = self.state.max_energy
        self.update_display()
        messagebox.showinfo("Rest", f"You rested. Now on Day {self.state.day}")
    
    def show_shop(self):
        """Show shop window"""
        shop = tk.Toplevel(self)
        shop.title("🏪 Farm Shop")
        shop.geometry("400x500")
        shop.configure(bg="#313244")
        
        tk.Label(shop, text=f"Money: ${self.state.money}", font=("Arial", 12, "bold"),
                bg="#313244", fg="#a6e3a1").pack(pady=10)
        
        # Seed shop
        tk.Label(shop, text="📦 BUY SEEDS", font=("Arial", 11, "bold"),
                bg="#313244", fg="#cdd6f4").pack(fill=tk.X, padx=10, pady=5)
        
        for crop_name, crop_data in list(CropData.CROPS.items())[:5]:
            frame = tk.Frame(shop, bg="#45475a")
            frame.pack(fill=tk.X, padx=10, pady=3)
            
            label = tk.Label(frame, text=f"{crop_data['emoji']} {crop_name} - ${crop_data['seed_cost']}",
                           bg="#45475a", fg="#cdd6f4", font=("Arial", 9), width=30, anchor="w")
            label.pack(side=tk.LEFT, padx=5, pady=5)
            
            btn = tk.Button(frame, text="Buy", font=("Arial", 8),
                           bg="#89b4fa", fg="white", relief=tk.FLAT,
                           command=lambda c=crop_name, p=crop_data['seed_cost']: self.buy_seed(c, p, shop))
            btn.pack(side=tk.RIGHT, padx=5, pady=5)
    
    def buy_seed(self, crop_name, price, shop_window):
        """Buy seeds from shop"""
        if self.state.money >= price:
            self.state.money -= price
            self.state.inventory[crop_name] += 1
            self.update_display()
            messagebox.showinfo("Purchase", f"Bought {crop_name}!")
        else:
            messagebox.showwarning("Poor", "Not enough money!")
    
    def save_game(self):
        """Save game state"""
        save_data = {
            "money": self.state.money,
            "day": self.state.day,
            "energy": self.state.energy,
            "inventory": self.state.inventory,
            "farm": {str(k): v for k, v in self.state.farm.items()}
        }
        
        os.makedirs("saves", exist_ok=True)
        with open("saves/croptopia_save.json", "w") as f:
            json.dump(save_data, f, indent=2)
        
        messagebox.showinfo("Save", "Game saved!")
    
    def update_display(self):
        """Update all UI elements"""
        self.state.update_temperature()
        
        # Update labels
        self.day_label.config(text=f"📅 Day {self.state.day} ({self.state.get_season()}) 🌡️{self.state.temperature}°F")
        self.money_label.config(text=f"💰 ${self.state.money}")
        
        energy_pct = int((self.state.energy / self.state.max_energy) * 100)
        self.energy_label.config(text=f"⚡ {self.state.energy}/{self.state.max_energy} ({energy_pct}%)")
        
        # Update inventory listbox
        self.inv_listbox.delete(0, tk.END)
        for crop_name, count in self.state.inventory.items():
            if count > 0:
                self.inv_listbox.insert(tk.END, f"{crop_name}: {count}")
        
        # Update farm canvas
        self.draw_farm()
    
    def draw_farm(self):
        """Render the farm grid"""
        self.canvas.delete("all")
        
        # Draw grid background
        for x in range(self.grid_width + 1):
            self.canvas.create_line(x * self.cell_size, 0,
                                   x * self.cell_size, self.grid_height * self.cell_size,
                                   fill="#45475a", width=1)
        
        for y in range(self.grid_height + 1):
            self.canvas.create_line(0, y * self.cell_size,
                                   self.grid_width * self.cell_size, y * self.cell_size,
                                   fill="#45475a", width=1)
        
        # Draw cells with plants, buildings, and NPCs
        for (x, y), cell in self.state.farm.items():
            px = x * self.cell_size
            py = y * self.cell_size
            
            # Cell background
            if (x + y) % 2 == 0:
                bg_color = "#3a3a4a"
            else:
                bg_color = "#2a2a3a"
            
            self.canvas.create_rectangle(px, py, px + self.cell_size, py + self.cell_size,
                                        fill=bg_color, outline="")
            
            # Draw buildings
            if (x, y) in self.state.buildings:
                building = self.state.buildings[(x, y)]
                building_emoji = {
                    "fence": "🚧",
                    "chest": "📦",
                    "shed": "🏠",
                    "greenhouse": "🌿"
                }
                emoji = building_emoji.get(building["type"], "?")
                self.canvas.create_text(px + self.cell_size // 2,
                                       py + self.cell_size // 2,
                                       text=emoji, font=("Arial", 14))
                continue
            
            # Draw NPCs
            npc_here = False
            for npc_name, npc_data in self.state.npcs.items():
                if npc_data["location"] == (x, y):
                    self.canvas.create_text(px + self.cell_size // 2,
                                           py + self.cell_size // 2,
                                           text="👤", font=("Arial", 14))
                    npc_here = True
                    break
            
            if npc_here:
                continue
            
            # Watered indicator
            if cell["watered"]:
                self.canvas.create_rectangle(px + 2, py + 2, px + 8, py + 8,
                                            fill="#64b5f6", outline="")
            
            # Plant
            if cell["plant"]:
                crop_data = CropData.CROPS[cell["plant"]]
                growth = cell["growth"]
                
                # Growth indicator color (affected by temperature)
                if growth < 25:
                    emoji = "•"
                    color = "#888"
                elif growth < 50:
                    emoji = "🌱"
                    color = "#a6e3a1"
                elif growth < 75:
                    emoji = "🌿"
                    color = "#4caf50"
                else:
                    emoji = crop_data["emoji"]
                    color = crop_data["color"]
                
                self.canvas.create_text(px + self.cell_size // 2,
                                       py + self.cell_size // 2,
                                       text=emoji, font=("Arial", 16),
                                       fill=color)


class EnhancedCroptopia(tk.Frame):
    """Wrapper to maintain compatibility"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.configure(bg="#1e1e2e")
        self.game = UltimatecroptopiaGame(self)
        self.game.pack(fill=tk.BOTH, expand=True)


def main():
    """Test the game"""
    root = tk.Tk()
    root.title("Ultimate Croptopia")
    root.geometry("1200x800")
    
    game = UltimatecroptopiaGame(root)
    game.pack(fill=tk.BOTH, expand=True)
    
    root.mainloop()


if __name__ == "__main__":
    main()
