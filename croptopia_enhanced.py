"""
Croptopia Enhanced - Farming Simulation Game
Inspired by the original Godot Croptopia game
Integrated into DoubOS
"""

import tkinter as tk
from tkinter import ttk, messagebox
import random
import json
from datetime import datetime


class EnhancedCroptopia(tk.Frame):
    """Enhanced Croptopia farming simulator with more features"""
    
    def __init__(self, parent):
        super().__init__(parent, bg="#2d5016")
        self.pack(fill=tk.BOTH, expand=True)
        
        # Game state
        self.money = 250
        self.day = 1
        self.season = "Spring"
        self.energy = 100
        self.max_energy = 100
        
        # Grid and crops
        self.grid_rows = 10
        self.grid_cols = 10
        self.cell_size = 50
        self.crops = {}  # {(row, col): crop_data}
        self.watered = set()  # Watered cells
        
        # Inventory system
        self.inventory = {
            # Crops
            "apple": 0, "carrot": 0, "wheat": 0, "potato": 0,
            "chive": 0, "sorrel": 0, "cranberry": 0,
            # Materials
            "stick": 0, "stone": 0, "wood": 0,
            # Seeds
            "apple_seed": 3, "carrot_seed": 5, "wheat_seed": 10,
            "potato_seed": 2, "chive_seed": 0, "sorrel_seed": 0, "cranberry_seed": 0
        }
        
        # Crop definitions (name, emoji, cost, days, sell_price, energy_cost)
        self.crop_types = {
            "apple": {"emoji": "🍎", "cost": 15, "days": 4, "sell": 25, "energy": 2, "seed": "apple_seed"},
            "carrot": {"emoji": "🥕", "cost": 10, "days": 3, "sell": 18, "energy": 1, "seed": "carrot_seed"},
            "wheat": {"emoji": "🌾", "cost": 5, "days": 2, "sell": 12, "energy": 1, "seed": "wheat_seed"},
            "potato": {"emoji": "🥔", "cost": 12, "days": 3, "sell": 20, "energy": 2, "seed": "potato_seed"},
            "chive": {"emoji": "🌿", "cost": 20, "days": 5, "sell": 35, "energy": 3, "seed": "chive_seed"},
            "sorrel": {"emoji": "🍀", "cost": 25, "days": 6, "sell": 42, "energy": 3, "seed": "sorrel_seed"},
            "cranberry": {"emoji": "🫐", "cost": 30, "days": 7, "sell": 55, "energy": 4, "seed": "cranberry_seed"},
        }
        
        self.selected_crop = "apple"
        self.tool_mode = "plant"  # plant, water, harvest, clear
        
        # Create UI
        self.setup_ui()
        
    def setup_ui(self):
        """Setup game UI"""
        # Top info bar
        info_frame = tk.Frame(self, bg="#1f3a0f", relief=tk.RIDGE, bd=2)
        info_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Left side stats
        left_stats = tk.Frame(info_frame, bg="#1f3a0f")
        left_stats.pack(side=tk.LEFT, padx=10, pady=8)
        
        self.day_label = tk.Label(left_stats, text=f"Day {self.day} - {self.season}",
                                  bg="#1f3a0f", fg="#a6e3a1",
                                  font=("Segoe UI", 11, "bold"))
        self.day_label.pack(side=tk.LEFT, padx=15)
        
        self.money_label = tk.Label(left_stats, text=f"💰 ${self.money}",
                                    bg="#1f3a0f", fg="#f1fa8c",
                                    font=("Segoe UI", 11, "bold"))
        self.money_label.pack(side=tk.LEFT, padx=15)
        
        self.energy_label = tk.Label(left_stats, text=f"⚡ {self.energy}/{self.max_energy}",
                                     bg="#1f3a0f", fg="#89b4fa",
                                     font=("Segoe UI", 11, "bold"))
        self.energy_label.pack(side=tk.LEFT, padx=15)
        
        # Main container
        main_container = tk.Frame(self, bg="#2d5016")
        main_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Left panel - Tools and crops
        left_panel = tk.Frame(main_container, bg="#1f3a0f", width=200, relief=tk.RIDGE, bd=2)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 5))
        left_panel.pack_propagate(False)
        
        tk.Label(left_panel, text="🛠️ Tools", bg="#1f3a0f", fg="#cdd6f4",
                font=("Segoe UI", 12, "bold")).pack(pady=(10, 5))
        
        tools = [
            ("🌱 Plant", "plant"),
            ("💧 Water", "water"),
            ("✂️ Harvest", "harvest"),
            ("🗑️ Clear", "clear")
        ]
        
        for tool_name, tool_id in tools:
            btn = tk.Button(left_panel, text=tool_name,
                           bg="#45475a", fg="#cdd6f4",
                           font=("Segoe UI", 9),
                           relief=tk.FLAT, cursor="hand2",
                           command=lambda t=tool_id: self.set_tool(t))
            btn.pack(fill=tk.X, padx=10, pady=3)
            
        tk.Label(left_panel, text="🌾 Crops", bg="#1f3a0f", fg="#cdd6f4",
                font=("Segoe UI", 12, "bold")).pack(pady=(15, 5))
        
        # Crop selection with seed count
        for crop_id, crop_data in self.crop_types.items():
            seed_count = self.inventory.get(crop_data["seed"], 0)
            btn_text = f"{crop_data['emoji']} {crop_id.title()} (${crop_data['cost']}) x{seed_count}"
            btn = tk.Button(left_panel, text=btn_text,
                           bg="#313244", fg="#cdd6f4",
                           font=("Segoe UI", 8),
                           relief=tk.FLAT, cursor="hand2",
                           command=lambda c=crop_id: self.select_crop(c))
            btn.pack(fill=tk.X, padx=10, pady=2)
        
        # Game canvas (center)
        canvas_frame = tk.Frame(main_container, bg="#2d5016")
        canvas_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        tk.Label(canvas_frame, text="🏡 Farm", bg="#2d5016", fg="#a6e3a1",
                font=("Segoe UI", 14, "bold")).pack(pady=5)
        
        self.canvas = tk.Canvas(canvas_frame, bg="#4a7c2f", 
                               highlightthickness=2, highlightbackground="#1f3a0f",
                               width=self.grid_cols * self.cell_size,
                               height=self.grid_rows * self.cell_size)
        self.canvas.pack(padx=10, pady=5)
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        
        # Right panel - Inventory and actions
        right_panel = tk.Frame(main_container, bg="#1f3a0f", width=220, relief=tk.RIDGE, bd=2)
        right_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(5, 0))
        right_panel.pack_propagate(False)
        
        tk.Label(right_panel, text="🎒 Inventory", bg="#1f3a0f", fg="#cdd6f4",
                font=("Segoe UI", 12, "bold")).pack(pady=(10, 5))
        
        # Scrollable inventory
        inv_canvas = tk.Canvas(right_panel, bg="#1f3a0f", height=300,
                              highlightthickness=0)
        scrollbar = tk.Scrollbar(right_panel, orient="vertical", command=inv_canvas.yview)
        self.inv_frame = tk.Frame(inv_canvas, bg="#1f3a0f")
        
        inv_canvas.create_window((0, 0), window=self.inv_frame, anchor="nw")
        inv_canvas.configure(yscrollcommand=scrollbar.set)
        
        inv_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.inv_frame.bind("<Configure>", lambda e: inv_canvas.configure(scrollregion=inv_canvas.bbox("all")))
        
        # Action buttons
        action_frame = tk.Frame(right_panel, bg="#1f3a0f")
        action_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=10)
        
        tk.Button(action_frame, text="💧 Water All ($5)",
                 bg="#89b4fa", fg="#1e1e2e",
                 font=("Segoe UI", 9, "bold"),
                 relief=tk.FLAT, cursor="hand2",
                 command=self.water_all).pack(fill=tk.X, padx=10, pady=3)
        
        tk.Button(action_frame, text="🌙 Next Day",
                 bg="#a6e3a1", fg="#1e1e2e",
                 font=("Segoe UI", 9, "bold"),
                 relief=tk.FLAT, cursor="hand2",
                 command=self.next_day).pack(fill=tk.X, padx=10, pady=3)
        
        tk.Button(action_frame, text="💤 Rest (Restore Energy)",
                 bg="#f9e2af", fg="#1e1e2e",
                 font=("Segoe UI", 9, "bold"),
                 relief=tk.FLAT, cursor="hand2",
                 command=self.rest).pack(fill=tk.X, padx=10, pady=3)
        
        tk.Button(action_frame, text="🛒 Shop",
                 bg="#f38ba8", fg="#1e1e2e",
                 font=("Segoe UI", 9, "bold"),
                 relief=tk.FLAT, cursor="hand2",
                 command=self.open_shop).pack(fill=tk.X, padx=10, pady=3)
        
        # Draw initial grid
        self.draw_grid()
        self.update_inventory_display()
        
    def draw_grid(self):
        """Draw the farm grid"""
        self.canvas.delete("all")
        
        # Draw grid cells
        for row in range(self.grid_rows):
            for col in range(self.grid_cols):
                x1 = col * self.cell_size
                y1 = row * self.cell_size
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size
                
                # Determine cell state
                cell_key = (row, col)
                is_watered = cell_key in self.watered
                has_crop = cell_key in self.crops
                
                # Cell background
                if is_watered:
                    color = "#3d5a28"  # Dark green for watered
                else:
                    color = "#5a8735"  # Normal green
                
                self.canvas.create_rectangle(x1, y1, x2, y2, 
                                            fill=color, outline="#2d4520", width=1)
                
                # Draw crop if exists
                if has_crop:
                    crop = self.crops[cell_key]
                    emoji = self.crop_types[crop["type"]]["emoji"]
                    days_grown = crop["days_grown"]
                    days_needed = self.crop_types[crop["type"]]["days"]
                    
                    # Show growth stage
                    if days_grown >= days_needed:
                        # Mature - full emoji
                        self.canvas.create_text(x1 + self.cell_size//2, y1 + self.cell_size//2,
                                              text=emoji, font=("Segoe UI Emoji", 24), fill="white")
                    elif days_grown >= days_needed * 0.66:
                        # 66% grown
                        self.canvas.create_text(x1 + self.cell_size//2, y1 + self.cell_size//2,
                                              text=emoji, font=("Segoe UI Emoji", 18), fill="#cdd6f4")
                    elif days_grown >= days_needed * 0.33:
                        # 33% grown
                        self.canvas.create_text(x1 + self.cell_size//2, y1 + self.cell_size//2,
                                              text="🌱", font=("Segoe UI Emoji", 14), fill="#a6e3a1")
                    else:
                        # Just planted
                        self.canvas.create_text(x1 + self.cell_size//2, y1 + self.cell_size//2,
                                              text="•", font=("Arial", 16, "bold"), fill="#89b4fa")
                    
                    # Show watered indicator
                    if is_watered:
                        self.canvas.create_text(x1 + 8, y1 + 8,
                                              text="💧", font=("Segoe UI Emoji", 8))
        
    def on_canvas_click(self, event):
        """Handle canvas click"""
        col = event.x // self.cell_size
        row = event.y // self.cell_size
        
        if 0 <= row < self.grid_rows and 0 <= col < self.grid_cols:
            cell_key = (row, col)
            
            if self.tool_mode == "plant":
                self.plant_crop(cell_key)
            elif self.tool_mode == "water":
                self.water_crop(cell_key)
            elif self.tool_mode == "harvest":
                self.harvest_crop(cell_key)
            elif self.tool_mode == "clear":
                self.clear_crop(cell_key)
    
    def set_tool(self, tool):
        """Set active tool"""
        self.tool_mode = tool
        
    def select_crop(self, crop_id):
        """Select crop to plant"""
        self.selected_crop = crop_id
        self.tool_mode = "plant"
        
    def plant_crop(self, cell_key):
        """Plant a crop"""
        if cell_key in self.crops:
            messagebox.showwarning("Croptopia", "There's already a crop here!")
            return
            
        crop_info = self.crop_types[self.selected_crop]
        seed_type = crop_info["seed"]
        
        # Check if we have seeds
        if self.inventory[seed_type] <= 0:
            messagebox.showwarning("Croptopia", f"You need {self.selected_crop} seeds!\nBuy them from the shop.")
            return
        
        # Check energy
        if self.energy < crop_info["energy"]:
            messagebox.showwarning("Croptopia", "Not enough energy! Rest to restore.")
            return
        
        # Plant the crop
        self.inventory[seed_type] -= 1
        self.energy -= crop_info["energy"]
        self.crops[cell_key] = {
            "type": self.selected_crop,
            "days_grown": 0,
            "watered_today": False
        }
        
        self.draw_grid()
        self.update_stats()
        self.update_inventory_display()
        
    def water_crop(self, cell_key):
        """Water a crop"""
        if cell_key not in self.crops:
            return
        
        if cell_key in self.watered:
            messagebox.showinfo("Croptopia", "Already watered today!")
            return
        
        self.watered.add(cell_key)
        self.crops[cell_key]["watered_today"] = True
        self.energy = max(0, self.energy - 1)
        
        self.draw_grid()
        self.update_stats()
        
    def harvest_crop(self, cell_key):
        """Harvest a mature crop"""
        if cell_key not in self.crops:
            return
        
        crop = self.crops[cell_key]
        crop_info = self.crop_types[crop["type"]]
        
        if crop["days_grown"] >= crop_info["days"]:
            # Harvest!
            self.inventory[crop["type"]] += 1
            self.energy = max(0, self.energy - 1)
            del self.crops[cell_key]
            if cell_key in self.watered:
                self.watered.remove(cell_key)
            
            messagebox.showinfo("Croptopia", f"Harvested {crop_info['emoji']} {crop['type'].title()}!")
            
            self.draw_grid()
            self.update_stats()
            self.update_inventory_display()
        else:
            messagebox.showwarning("Croptopia", "Crop is not ready to harvest yet!")
            
    def clear_crop(self, cell_key):
        """Clear a crop (remove it)"""
        if cell_key in self.crops:
            del self.crops[cell_key]
            if cell_key in self.watered:
                self.watered.remove(cell_key)
            self.draw_grid()
            
    def water_all(self):
        """Water all crops (costs money)"""
        if len(self.crops) == 0:
            messagebox.showinfo("Croptopia", "No crops to water!")
            return
        
        if self.money < 5:
            messagebox.showwarning("Croptopia", "Not enough money to water all! (Costs $5)")
            return
        
        self.money -= 5
        for cell_key in self.crops:
            self.watered.add(cell_key)
            self.crops[cell_key]["watered_today"] = True
        
        self.draw_grid()
        self.update_stats()
        
    def next_day(self):
        """Advance to next day"""
        # Grow watered crops
        grown_count = 0
        for cell_key, crop in self.crops.items():
            if crop["watered_today"]:
                crop["days_grown"] += 1
                grown_count += 1
        
        # Reset watered status
        self.watered.clear()
        for crop in self.crops.values():
            crop["watered_today"] = False
        
        # Advance day
        self.day += 1
        
        # Change season every 28 days
        if self.day % 28 == 1:
            seasons = ["Spring", "Summer", "Fall", "Winter"]
            self.season = seasons[(self.day // 28) % 4]
        
        # Restore some energy
        self.energy = min(self.max_energy, self.energy + 20)
        
        messagebox.showinfo("Croptopia", f"Day {self.day} - {grown_count} crops grew!")
        
        self.draw_grid()
        self.update_stats()
        
    def rest(self):
        """Rest to restore energy"""
        if self.energy >= self.max_energy:
            messagebox.showinfo("Croptopia", "Energy already full!")
            return
        
        self.energy = self.max_energy
        messagebox.showinfo("Croptopia", "Energy fully restored!")
        self.update_stats()
        
    def open_shop(self):
        """Open the shop"""
        shop = tk.Toplevel(self.winfo_toplevel())
        shop.title("🛒 Croptopia Shop")
        shop.geometry("400x500")
        shop.configure(bg="#1f3a0f")
        
        tk.Label(shop, text="🛒 Shop", bg="#1f3a0f", fg="#a6e3a1",
                font=("Segoe UI", 16, "bold")).pack(pady=10)
        
        tk.Label(shop, text=f"Your Money: ${self.money}", bg="#1f3a0f", fg="#f1fa8c",
                font=("Segoe UI", 12)).pack(pady=5)
        
        # Shop items
        shop_frame = tk.Frame(shop, bg="#1f3a0f")
        shop_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Seeds
        tk.Label(shop_frame, text="Seeds:", bg="#1f3a0f", fg="#cdd6f4",
                font=("Segoe UI", 11, "bold")).pack(anchor=tk.W, pady=(5, 5))
        
        for crop_id, crop_data in self.crop_types.items():
            item_frame = tk.Frame(shop_frame, bg="#313244", relief=tk.RIDGE, bd=1)
            item_frame.pack(fill=tk.X, pady=3)
            
            tk.Label(item_frame, text=f"{crop_data['emoji']} {crop_id.title()} Seed - ${crop_data['cost']}",
                    bg="#313244", fg="#cdd6f4", font=("Segoe UI", 9)).pack(side=tk.LEFT, padx=10, pady=5)
            
            tk.Button(item_frame, text="Buy",
                     bg="#a6e3a1", fg="#1e1e2e",
                     font=("Segoe UI", 8, "bold"),
                     relief=tk.FLAT, cursor="hand2",
                     command=lambda c=crop_id: self.buy_seed(c, shop)).pack(side=tk.RIGHT, padx=10, pady=5)
        
        # Sell crops
        tk.Label(shop_frame, text="Sell Crops:", bg="#1f3a0f", fg="#cdd6f4",
                font=("Segoe UI", 11, "bold")).pack(anchor=tk.W, pady=(15, 5))
        
        for crop_id, crop_data in self.crop_types.items():
            count = self.inventory.get(crop_id, 0)
            if count > 0:
                item_frame = tk.Frame(shop_frame, bg="#313244", relief=tk.RIDGE, bd=1)
                item_frame.pack(fill=tk.X, pady=3)
                
                tk.Label(item_frame, text=f"{crop_data['emoji']} {crop_id.title()} x{count} - Sell for ${crop_data['sell']}",
                        bg="#313244", fg="#cdd6f4", font=("Segoe UI", 9)).pack(side=tk.LEFT, padx=10, pady=5)
                
                tk.Button(item_frame, text="Sell",
                         bg="#f1fa8c", fg="#1e1e2e",
                         font=("Segoe UI", 8, "bold"),
                         relief=tk.FLAT, cursor="hand2",
                         command=lambda c=crop_id: self.sell_crop(c, shop)).pack(side=tk.RIGHT, padx=10, pady=5)
        
    def buy_seed(self, crop_id, shop_window):
        """Buy a seed"""
        crop_data = self.crop_types[crop_id]
        if self.money >= crop_data["cost"]:
            self.money -= crop_data["cost"]
            self.inventory[crop_data["seed"]] += 1
            self.update_stats()
            self.update_inventory_display()
            
            # Update shop display
            shop_window.destroy()
            self.open_shop()
        else:
            messagebox.showwarning("Shop", "Not enough money!")
            
    def sell_crop(self, crop_id, shop_window):
        """Sell a crop"""
        if self.inventory[crop_id] > 0:
            crop_data = self.crop_types[crop_id]
            self.inventory[crop_id] -= 1
            self.money += crop_data["sell"]
            self.update_stats()
            self.update_inventory_display()
            
            # Update shop display
            shop_window.destroy()
            self.open_shop()
        else:
            messagebox.showwarning("Shop", "You don't have any to sell!")
            
    def update_stats(self):
        """Update stat labels"""
        self.day_label.configure(text=f"Day {self.day} - {self.season}")
        self.money_label.configure(text=f"💰 ${self.money}")
        self.energy_label.configure(text=f"⚡ {self.energy}/{self.max_energy}")
        
    def update_inventory_display(self):
        """Update inventory display"""
        # Clear existing
        for widget in self.inv_frame.winfo_children():
            widget.destroy()
        
        # Display inventory items
        for item, count in sorted(self.inventory.items()):
            if count > 0:
                # Get emoji
                emoji = ""
                if "_seed" in item:
                    crop_name = item.replace("_seed", "")
                    if crop_name in self.crop_types:
                        emoji = self.crop_types[crop_name]["emoji"] + "🌱"
                    item_display = item.replace("_", " ").title()
                elif item in self.crop_types:
                    emoji = self.crop_types[item]["emoji"]
                    item_display = item.title()
                else:
                    emoji = "📦"
                    item_display = item.replace("_", " ").title()
                
                item_frame = tk.Frame(self.inv_frame, bg="#313244", relief=tk.FLAT)
                item_frame.pack(fill=tk.X, pady=2, padx=5)
                
                tk.Label(item_frame, text=f"{emoji} {item_display}: {count}",
                        bg="#313244", fg="#cdd6f4",
                        font=("Segoe UI", 9)).pack(anchor=tk.W, padx=8, pady=3)
