"""
Croptopia - Farming Simulation Game
Integrated into DoubOS Games
"""

import tkinter as tk
from tkinter import messagebox
import random
import json


class CroptopiaSim(tk.Frame):
    """Croptopia farming simulator"""
    
    def __init__(self, parent, colors=None):
        super().__init__(parent, bg="#2d5016")
        self.colors = colors or {}
        self.pack(fill=tk.BOTH, expand=True)
        
        # Game state
        self.money = 100
        self.day = 1
        self.crops = {}
        self.inventory = {"apple": 0, "carrot": 0, "wheat": 0}
        self.selected_crop = "apple"
        
        # Create UI
        self.setup_ui()
        self.setup_game()
        
    def setup_ui(self):
        """Setup game UI"""
        # Top info bar
        info_frame = tk.Frame(self, bg="#1f3a0f")
        info_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.day_label = tk.Label(info_frame, text=f"Day: {self.day}",
                                  bg="#1f3a0f", fg="#a6e3a1",
                                  font=("Segoe UI", 12, "bold"))
        self.day_label.pack(side=tk.LEFT, padx=20)
        
        self.money_label = tk.Label(info_frame, text=f"Money: ${self.money}",
                                    bg="#1f3a0f", fg="#f1fa8c",
                                    font=("Segoe UI", 12, "bold"))
        self.money_label.pack(side=tk.LEFT, padx=20)
        
        # Game canvas
        self.canvas = tk.Canvas(self, bg="#2d5016", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        
        # Controls
        control_frame = tk.Frame(self, bg="#1f3a0f")
        control_frame.pack(fill=tk.X, padx=10, pady=10)
        
        crops = [
            ("🍎 Apple", "apple", "red"),
            ("🥕 Carrot", "carrot", "orange"),
            ("🌾 Wheat", "wheat", "gold")
        ]
        
        for label, crop, color in crops:
            btn = tk.Button(control_frame, text=label,
                           bg=color, fg="black",
                           font=("Segoe UI", 10, "bold"),
                           command=lambda c=crop: self.select_crop(c),
                           width=12)
            btn.pack(side=tk.LEFT, padx=5)
        
        # Inventory
        inv_frame = tk.Frame(self, bg="#1f3a0f")
        inv_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        tk.Label(inv_frame, text="Inventory:", bg="#1f3a0f",
                fg="#cdd6f4", font=("Segoe UI", 10)).pack(side=tk.LEFT, padx=5)
        
        self.inv_label = tk.Label(inv_frame, text="",
                                 bg="#1f3a0f", fg="#cdd6f4",
                                 font=("Segoe UI", 9))
        self.inv_label.pack(side=tk.LEFT, padx=5)
        
        # Action buttons
        action_frame = tk.Frame(self, bg="#1f3a0f")
        action_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        tk.Button(action_frame, text="⏭️ Next Day", bg="#89b4fa", fg="black",
                 font=("Segoe UI", 10, "bold"),
                 command=self.next_day).pack(side=tk.LEFT, padx=5)
        
        tk.Button(action_frame, text="🌾 Water All", bg="#7aa2f7", fg="black",
                 font=("Segoe UI", 10, "bold"),
                 command=self.water_all).pack(side=tk.LEFT, padx=5)
        
    def setup_game(self):
        """Setup game board"""
        self.draw_board()
        
    def draw_board(self):
        """Draw game board"""
        self.canvas.delete("all")
        
        # Grid
        cell_size = 60
        cols, rows = 8, 6
        
        for row in range(rows):
            for col in range(cols):
                x1 = col * cell_size
                y1 = row * cell_size
                x2 = x1 + cell_size
                y2 = y1 + cell_size
                
                # Cell background
                self.canvas.create_rectangle(x1, y1, x2, y2,
                                            fill="#3d6b1f", outline="#2d5016",
                                            width=2)
                
                # Check if crop here
                cell_id = f"{row},{col}"
                if cell_id in self.crops:
                    crop_info = self.crops[cell_id]
                    crop_type = crop_info["type"]
                    age = crop_info["age"]
                    watered = crop_info.get("watered", False)
                    
                    # Draw crop
                    emoji = {"apple": "🍎", "carrot": "🥕", "wheat": "🌾"}[crop_type]
                    self.canvas.create_text(x1 + cell_size//2, y1 + cell_size//2,
                                           text=emoji, font=("Segoe UI", 30))
                    
                    # Age indicator
                    self.canvas.create_text(x1 + 5, y1 + 5,
                                           text=f"D{age}", anchor="nw",
                                           fill="white", font=("Segoe UI", 8))
                    
                    # Water indicator
                    if watered:
                        self.canvas.create_oval(x1 + 45, y1 + 45, x1 + 55, y1 + 55,
                                               fill="#4a9eff")
                        
    def on_canvas_click(self, event):
        """Handle canvas click"""
        cell_size = 60
        cols = 8
        
        col = event.x // cell_size
        row = event.y // cell_size
        
        if 0 <= row < 6 and 0 <= col < cols:
            cell_id = f"{row},{col}"
            
            if cell_id in self.crops:
                # Harvest crop
                crop_info = self.crops[cell_id]
                if crop_info["age"] >= 3:  # Mature
                    self.harvest(cell_id, crop_info)
                else:
                    messagebox.showinfo("Not Ready", "Crop not ready yet!")
            else:
                # Plant crop
                if self.money >= 10:
                    self.plant_crop(cell_id)
                else:
                    messagebox.showerror("No Money", "Need $10 to plant!")
                    
    def plant_crop(self, cell_id):
        """Plant a crop"""
        self.crops[cell_id] = {
            "type": self.selected_crop,
            "age": 0,
            "watered": True
        }
        self.money -= 10
        self.update_ui()
        self.draw_board()
        
    def harvest(self, cell_id, crop_info):
        """Harvest a crop"""
        crop_type = crop_info["type"]
        self.inventory[crop_type] += 1
        
        # Earn money
        earnings = {"apple": 15, "carrot": 12, "wheat": 10}
        self.money += earnings[crop_type]
        
        del self.crops[cell_id]
        self.update_ui()
        self.draw_board()
        
    def select_crop(self, crop):
        """Select crop to plant"""
        self.selected_crop = crop
        
    def water_all(self):
        """Water all crops"""
        for crop_info in self.crops.values():
            crop_info["watered"] = True
        self.draw_board()
        
    def next_day(self):
        """Advance to next day"""
        self.day += 1
        
        # Grow crops
        for crop_info in self.crops.values():
            if crop_info.get("watered", False):
                crop_info["age"] += 1
            crop_info["watered"] = False
        
        self.update_ui()
        self.draw_board()
        
    def update_ui(self):
        """Update UI labels"""
        self.day_label.config(text=f"Day: {self.day}")
        self.money_label.config(text=f"Money: ${self.money}")
        
        inv_text = " | ".join([f"{k.title()}: {v}" for k, v in self.inventory.items()])
        self.inv_label.config(text=inv_text)
