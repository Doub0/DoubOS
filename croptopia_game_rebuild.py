"""
Croptopia Game Engine - Complete Rebuild
Version: 2.0
Purpose: Python-based Croptopia game using actual Godot structure from Croptopia - 02.11.25

ARCHITECTURE OVERVIEW:
- Zone-based system: world_2 (spawn), shelburne (town), caves (mining)
- Real asset loading from PNG files
- Proper scene hierarchy matching Godot TSCN structure
- Player movement with 4-directional animation
- Inventory and item collection system
- NPC and dialogue framework
- Day/night cycle
- Crop growth mechanics
- Economy/trading system

KEY IMPROVEMENTS FROM PREVIOUS VERSION:
1. Real asset paths from croptopia_assets/
2. Proper scene management instead of monolithic world
3. Zone transitions with entry/exit points
4. Real crop growth timing (parsed from GD scripts)
5. Actual NPC locations and merchants
6. Working inventory with signals
7. Day/night cycle implementation
"""

import os
import json
import time
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Set
import random
from PIL import Image, ImageDraw
import tkinter as tk
from tkinter import Canvas as TkCanvas
import threading

# ============================================================================
# CONFIGURATION & PATHS
# ============================================================================

CROPTOPIA_PATH = r"c:\Users\Jonas\Documents\doubOS\DoubOS\Croptopia - 02.11.25"
ASSETS_PATH = os.path.join(CROPTOPIA_PATH, "assets")
SCENES_PATH = os.path.join(CROPTOPIA_PATH, "scenes")

# Window dimensions
WINDOW_WIDTH = 1920
WINDOW_HEIGHT = 1080

# Game tick rate
FPS = 60
TICK_TIME = 1.0 / FPS

# ============================================================================
# ENUMS & DATA CLASSES
# ============================================================================

class Direction(Enum):
    """Player movement directions"""
    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)
    NONE = (0, 0)

class ItemType(Enum):
    """Item category types"""
    CONSUMABLE = "consumable"
    TOOL = "tool"
    RESOURCE = "resource"
    CROP = "crop"
    SEED = "seed"

class CropStage(Enum):
    """Crop growth stages matching wheat.gd"""
    NO_CROP = "no_crop"
    STAGE_1 = "stage_1"
    STAGE_2 = "stage_2"
    STAGE_3 = "stage_3"
    STAGE_4 = "stage_4"
    HARVESTABLE = "harvestable"

@dataclass
class Vector2:
    """2D vector for positions"""
    x: float
    y: float
    
    def __add__(self, other):
        return Vector2(self.x + other.x, self.y + other.y)
    
    def __sub__(self, other):
        return Vector2(self.x - other.x, self.y - other.y)
    
    def tuple(self) -> Tuple[float, float]:
        return (self.x, self.y)

@dataclass
class Item:
    """Base item in inventory"""
    name: str
    item_type: ItemType
    icon_path: Optional[str] = None
    description: str = ""
    value: int = 1  # Trade value
    stackable: bool = False
    max_stack: int = 1
    
    def __hash__(self):
        return hash((self.name, self.item_type.value))
    
    def __eq__(self, other):
        return self.name == other.name and self.item_type == other.item_type

@dataclass
class CropData:
    """Crop definition with growth stages and yields"""
    name: str
    growth_times: List[float]  # Time in seconds for each stage (matches GD timers)
    harvestable_item: Item
    seed_cost: int = 0
    requires_tilling: bool = True
    animation_frames: List[str] = field(default_factory=list)
    
    def get_total_growth_time(self) -> float:
        """Total time from plant to harvest"""
        return sum(self.growth_times)

@dataclass
class NPCData:
    """NPC definition"""
    name: str
    position: Vector2
    sprite_path: Optional[str] = None
    dialogue_lines: List[str] = field(default_factory=list)
    trades: Dict[Item, int] = field(default_factory=dict)  # Item -> price
    quest_stage: int = 0
    location_zone: str = "shelburne"

@dataclass
class ZoneData:
    """Zone/scene definition"""
    name: str
    tilemap_width: int
    tilemap_height: int
    background_png: Optional[str] = None
    spawn_position: Vector2 = field(default_factory=lambda: Vector2(100, 100))
    collectable_items: List[Tuple[Vector2, Item]] = field(default_factory=list)
    npcs: List[NPCData] = field(default_factory=list)
    crops_planted: Dict[Tuple[int, int], CropData] = field(default_factory=dict)
    zone_transitions: Dict[str, Vector2] = field(default_factory=dict)  # zone_name -> position

# ============================================================================
# ASSET MANAGEMENT
# ============================================================================

class AssetManager:
    """Manages loading and caching of PNG assets"""
    
    def __init__(self, assets_path: str):
        self.assets_path = assets_path
        self._image_cache: Dict[str, Image.Image] = {}
        self._failed_assets: Set[str] = set()
    
    def load_image(self, filename: str) -> Optional[Image.Image]:
        """Load PNG image with caching"""
        if filename in self._image_cache:
            return self._image_cache[filename]
        
        if filename in self._failed_assets:
            return None
        
        # Try multiple paths: assets/, root, animations/, scenes/
        possible_paths = [
            os.path.join(self.assets_path, filename),
            os.path.join(CROPTOPIA_PATH, filename),
            os.path.join(CROPTOPIA_PATH, "animations", filename),
            os.path.join(CROPTOPIA_PATH, "scenes", filename),
            os.path.join(CROPTOPIA_PATH, "pixilart-frames", filename),
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                try:
                    img = Image.open(path)
                    self._image_cache[filename] = img
                    return img
                except Exception as e:
                    print(f"Failed to load {path}: {e}")
        
        self._failed_assets.add(filename)
        return None
    
    def get_asset_or_placeholder(self, filename: str, width: int = 32, height: int = 32) -> Image.Image:
        """Get image or create placeholder"""
        img = self.load_image(filename)
        if img:
            return img
        
        # Create placeholder
        placeholder = Image.new('RGBA', (width, height), (128, 128, 128, 255))
        return placeholder
    
    def list_assets(self, pattern: str = "*.png") -> List[str]:
        """List available assets"""
        assets = []
        if os.path.exists(self.assets_path):
            for f in os.listdir(self.assets_path):
                if f.endswith(".png"):
                    assets.append(f)
        return assets

# ============================================================================
# INVENTORY & ITEMS SYSTEM
# ============================================================================

class Inventory:
    """Player inventory system with signals"""
    
    def __init__(self, max_slots: int = 20):
        self.max_slots = max_slots
        self.items: List[Item] = []
        self.observers: List[callable] = []
    
    def insert(self, item: Item) -> bool:
        """Add item to inventory, emit signal"""
        if len(self.items) < self.max_slots:
            self.items.append(item)
            self._notify_observers("item_added", item)
            return True
        return False
    
    def remove(self, item: Item) -> bool:
        """Remove item from inventory"""
        if item in self.items:
            self.items.remove(item)
            self._notify_observers("item_removed", item)
            return True
        return False
    
    def get_item_count(self, item: Item) -> int:
        """Count of specific item in inventory"""
        return sum(1 for i in self.items if i == item)
    
    def on_change(self, callback: callable):
        """Subscribe to inventory changes"""
        self.observers.append(callback)
    
    def _notify_observers(self, event: str, item: Item):
        """Trigger signal-like notifications"""
        for observer in self.observers:
            observer(event, item)

# ============================================================================
# CROP SYSTEM (From actual GD scripts)
# ============================================================================

class CropSystem:
    """Manages crop growth and harvesting"""
    
    # Growth times in seconds based on GD timers
    CROP_DEFINITIONS = {
        # Original crops
        "wheat": CropData(
            name="Wheat",
            growth_times=[5.0, 5.0, 5.0, 5.0],  # 4 stages, 20 seconds total
            harvestable_item=Item("Wheat", ItemType.CROP, "wheat.png", "Harvested wheat", 1),
            requires_tilling=True
        ),
        "potato": CropData(
            name="Potato",
            growth_times=[6.0, 6.0, 6.0, 6.0],
            harvestable_item=Item("Potato", ItemType.CROP, "potato_crop.png", "Harvested potato", 2),
            requires_tilling=True
        ),
        "chive": CropData(
            name="Chive",
            growth_times=[4.0, 4.0, 4.0, 4.0],
            harvestable_item=Item("Chive", ItemType.CROP, "chive.png", "Fresh chive", 1),
            requires_tilling=True
        ),
        # New crops from ideaboard
        "white_pine": CropData(
            name="White Pine",
            growth_times=[10.0, 10.0, 10.0, 10.0],
            harvestable_item=Item("White Pinecone", ItemType.CROP, "white_pinecone.png", "Unique pinecone", 3),
            requires_tilling=False
        ),
        "wild_raisin": CropData(
            name="Wild Raisin",
            growth_times=[8.0, 8.0, 8.0, 8.0],
            harvestable_item=Item("Wild Raisin", ItemType.CROP, "wild_raisin.png", "Sweet raisin", 2),
            requires_tilling=True
        ),
        "red_baneberry": CropData(
            name="Red Baneberry",
            growth_times=[7.0, 7.0, 7.0, 7.0],
            harvestable_item=Item("Red Baneberry", ItemType.CROP, "red_baneberry.png", "Baneberry", 1),
            requires_tilling=True
        ),
        "elderberry": CropData(
            name="Elderberry",
            growth_times=[9.0, 9.0, 9.0, 9.0],
            harvestable_item=Item("Elderberry", ItemType.CROP, "elderberry.png", "Elderberry", 1),
            requires_tilling=False
        ),
        "sorrel": CropData(
            name="Sorrel",
            growth_times=[5.0, 5.0, 5.0, 5.0],
            harvestable_item=Item("Sorrel", ItemType.CROP, "sorrel.png", "Sorrel leaf", 1),
            requires_tilling=True
        ),
    }
    
    def __init__(self):
        self.crops_growing: Dict[str, Tuple[CropData, float]] = {}  # id -> (crop, time_elapsed)
    
    def plant_crop(self, crop_id: str, crop_type: str) -> bool:
        """Plant a crop, track growth"""
        if crop_type not in self.CROP_DEFINITIONS:
            return False
        
        crop_data = self.CROP_DEFINITIONS[crop_type]
        self.crops_growing[crop_id] = (crop_data, 0.0)
        return True
    
    def update(self, delta: float):
        """Update crop growth times"""
        to_harvest = []
        for crop_id, (crop_data, elapsed) in self.crops_growing.items():
            elapsed += delta
            if elapsed >= crop_data.get_total_growth_time():
                to_harvest.append(crop_id)
            else:
                self.crops_growing[crop_id] = (crop_data, elapsed)
        
        for crop_id in to_harvest:
            crop_data, _ = self.crops_growing[crop_id]
            del self.crops_growing[crop_id]
            # Trigger harvest
    
    def get_crop_stage(self, crop_id: str) -> CropStage:
        """Get current growth stage of crop"""
        if crop_id not in self.crops_growing:
            return CropStage.NO_CROP
        
        crop_data, elapsed = self.crops_growing[crop_id]
        total_time = crop_data.get_total_growth_time()
        
        if elapsed >= total_time:
            return CropStage.HARVESTABLE
        
        # Calculate stage
        stage_time = total_time / 4
        stage = int(elapsed / stage_time) + 1
        
        if stage == 1:
            return CropStage.STAGE_1
        elif stage == 2:
            return CropStage.STAGE_2
        elif stage == 3:
            return CropStage.STAGE_3
        else:
            return CropStage.STAGE_4

# ============================================================================
# ITEM DATABASE (From ideaboard)
# ============================================================================

class ItemDatabase:
    """All items available in the game"""
    
    # Resources from ideaboard
    RESOURCES = {
        "coal": Item("Coal", ItemType.RESOURCE, "coal.png", "Raw coal", 5),
        "iron": Item("Raw Iron", ItemType.RESOURCE, "raw_iron.png", "Raw iron ore", 10),
        "iron_ingot": Item("Iron Ingot", ItemType.RESOURCE, "iron_ingot.png", "Smelted iron", 15),
        "logs": Item("Logs", ItemType.RESOURCE, "logs.png", "Tree logs", 3),
        "sap": Item("Tree Sap", ItemType.RESOURCE, "sap.png", "Sticky tree sap", 4),
        "water": Item("Water", ItemType.RESOURCE, "water.png", "Fresh water", 1),
        "grass_strands": Item("Grass Strands", ItemType.RESOURCE, "grass_strands.png", "Plant fibers", 2),
        "bio_string": Item("Bio String", ItemType.RESOURCE, "bio_string.png", "Woven plant string", 5),
        "wool": Item("Wool", ItemType.RESOURCE, "wool.png", "Sheep wool", 8),
        "stone": Item("Stone", ItemType.RESOURCE, "stone.png", "Raw stone", 2),
        "pinecone": Item("Pinecone", ItemType.RESOURCE, "pinecone.png", "Standard pinecone", 1),
    }
    
    # Tools from ideaboard
    TOOLS = {
        "shovel": Item("Shovel", ItemType.TOOL, "shovel.png", "Digging tool", 5),
        "axe": Item("Axe", ItemType.TOOL, "axe.png", "Chopping tool", 10),
        "tapper": Item("Tapper", ItemType.TOOL, "tapper.png", "Sap extraction tool", 8),
        "rake": Item("Rake", ItemType.TOOL, "rake.png", "Grass collection tool", 6),
        "fishing_rod": Item("Fishing Rod", ItemType.TOOL, "fishing_rod.png", "For fishing", 25),
        "hammer": Item("Hammer", ItemType.TOOL, "hammer.png", "Building tool", 12),
    }
    
    # Paints from ideaboard
    PAINTS = {
        "red_paint": Item("Red Paint", ItemType.RESOURCE, "red_paint.png", "Red dye", 2),
        "blue_paint": Item("Blue Paint", ItemType.RESOURCE, "blue_paint.png", "Blue dye", 2),
        "yellow_paint": Item("Yellow Paint", ItemType.RESOURCE, "yellow_paint.png", "Yellow dye", 2),
        "white_paint": Item("White Paint", ItemType.RESOURCE, "white_paint.png", "White dye", 2),
        "brown_paint": Item("Brown Paint", ItemType.RESOURCE, "brown_paint.png", "Brown dye", 2),
    }
    
    # Buildables from ideaboard
    BUILDABLES = {
        "wooden_wall": Item("Wooden Wall", ItemType.RESOURCE, "wooden_wall.png", "Building material", 15),
        "wooden_fence": Item("Wooden Fence", ItemType.RESOURCE, "wooden_fence.png", "Fence segment", 12),
        "road_dark": Item("Dark Road", ItemType.RESOURCE, "road_dark.png", "Road tile", 5),
        "road_light": Item("Light Road", ItemType.RESOURCE, "road_light.png", "Road tile", 5),
        "building_frame": Item("Building Frame", ItemType.RESOURCE, "building_frame.png", "Plot for construction", 100),
    }
    
    # Tradeable items from ideaboard
    TRADEABLE = {
        "lantern": Item("Lantern", ItemType.RESOURCE, "lantern.png", "Light source", 1),
        "crucifix": Item("Crucifix", ItemType.RESOURCE, "crucifix.png", "Luck charm", 10),
    }
    
    # Alcohol from ideaboard
    ALCOHOL = {
        "beer": Item("Beer", ItemType.CONSUMABLE, "beer.png", "Alcoholic beverage, +15 DRPS", 8),
        "mead": Item("Mead", ItemType.CONSUMABLE, "mead.png", "Honey wine, +15 DRPS", 10),
        "hunters_liquor": Item("Hunter's Liquor", ItemType.CONSUMABLE, "hunters_liquor.png", "Strong spirit, +50 DRPS", 20),
        "red_wine": Item("Red Wine", ItemType.CONSUMABLE, "red_wine.png", "Fine wine, +5 DRPS", 12),
        "vodka": Item("Vodka", ItemType.CONSUMABLE, "vodka.png", "Clear spirit, +85 DRPS", 25),
        "whiskey": Item("Whiskey", ItemType.CONSUMABLE, "whiskey.png", "Aged spirit, +75 DRPS", 22),
    }
    
    @classmethod
    def get_all_items(cls):
        """Get all items as a dictionary"""
        return {
            **cls.RESOURCES,
            **cls.TOOLS,
            **cls.PAINTS,
            **cls.BUILDABLES,
            **cls.TRADEABLE,
            **cls.ALCOHOL,
        }



# ============================================================================
# ECONOMY SYSTEM (From economy_manager.gd)
# ============================================================================

class EconomyManager:
    """Manages pricing and inflation from GD script"""
    
    def __init__(self):
        self.base_prices: Dict[str, int] = {
            "elderberry": 1,
            "pinecone": 1,
            "sorrel": 1,
            "chive": 1,
            "baneberry": 1.5,
        }
        self.inflation = 1.0
        self.demand_state = "neutral"
        self.price = 1
    
    def update_inflation(self):
        """Simulate inflation fluctuation"""
        inflation_value = random.uniform(-0.1, 1.3)
        self.inflation = round(inflation_value, 2)
        
        if self.inflation > 0.75:
            self.demand_state = "high demand"
        elif self.inflation < 0.25:
            self.demand_state = "low demand"
        else:
            self.demand_state = "neutral"
        
        self.price = int(self.base_prices.get("chive", 1) * self.inflation)
    
    def get_item_price(self, item_name: str) -> int:
        """Get current price of item"""
        base = self.base_prices.get(item_name, 1)
        return int(base * self.inflation)

# ============================================================================
# ALCOHOL & DRUNKENNESS SYSTEM (From ideaboard)
# ============================================================================

class DrunkennessSystem:
    """Manage alcohol consumption and drunkenness effects"""
    
    MAX_DRPS = 100  # Drunk points
    
    def __init__(self):
        self.drps = 0  # Current drunk points
        self.is_drunk = False
        self.permanent_nerfs = {
            "movement_speed": 0,  # -20 if over max
            "health": 0,  # -20 if over max
            "tool_swing_speed": 1.0,  # Slower if drunk
        }
    
    def consume_alcohol(self, drps_value: int):
        """Consume alcohol and add drunk points"""
        self.drps += drps_value
        
        if self.drps >= self.MAX_DRPS:
            self.is_drunk = True
            # Apply permanent nerfs (reset each day ideally)
            self.permanent_nerfs["movement_speed"] = -20
            self.permanent_nerfs["health"] = -20
            self.permanent_nerfs["tool_swing_speed"] = 0.7
    
    def sober_up(self, amount: int = 10):
        """Reduce drunk points"""
        self.drps = max(0, self.drps - amount)
        if self.drps < self.MAX_DRPS:
            self.is_drunk = False
    
    def get_movement_modifier(self) -> float:
        """Get movement speed multiplier when drunk"""
        if self.is_drunk:
            return 0.5  # 50% speed when drunk
        return 1.0
    
    def get_random_direction(self) -> Direction:
        """When drunk, randomly choose direction instead of intended"""
        if self.is_drunk:
            return random.choice(list(Direction))
        return Direction.NONE

# ============================================================================
# LUCK SYSTEM (From ideaboard)
# ============================================================================

class LuckSystem:
    """Manage player luck for rare item drops and effects"""
    
    def __init__(self):
        self.luck_points = 0
        self.has_crucifix = False
        self.church_blessing_cooldown = 0  # days
        self.church_blessing_active = False
    
    def add_luck_points(self, amount: int):
        """Add luck points (max 20 from church, +10 from crucifix)"""
        self.luck_points = min(self.luck_points + amount, 30)
    
    def visit_church(self) -> bool:
        """Visit church for blessing, +20 luck, 3 day cooldown"""
        if self.church_blessing_cooldown <= 0:
            self.add_luck_points(20)
            self.church_blessing_cooldown = 3  # 3 game days
            self.church_blessing_active = True
            return True
        return False
    
    def get_rare_drop_chance(self) -> float:
        """Get chance for rare drops based on luck"""
        # Base 10% chance, +1% per luck point (max 40%)
        return min(0.10 + (self.luck_points * 0.01), 0.40)
    
    def update_day(self):
        """Called each day to decrease cooldowns"""
        if self.church_blessing_cooldown > 0:
            self.church_blessing_cooldown -= 1

# ============================================================================
# CRAFTING SYSTEM (From ideaboard)
# ============================================================================

class CraftingSystem:
    """Manage recipes and crafting"""
    
    RECIPES = {
        "wooden_wall": {
            "name": "Wooden Wall",
            "ingredients": {"logs": 5, "bio_string": 2},
            "output": "wooden_wall",
            "output_quantity": 1,
        },
        "wooden_fence": {
            "name": "Wooden Fence",
            "ingredients": {"logs": 3, "bio_string": 1},
            "output": "wooden_fence",
            "output_quantity": 1,
        },
        "shovel": {
            "name": "Shovel",
            "ingredients": {"logs": 3, "iron_ingot": 1, "bio_string": 2},
            "output": "shovel",
            "output_quantity": 1,
        },
        "axe": {
            "name": "Axe",
            "ingredients": {"logs": 4, "iron_ingot": 2, "bio_string": 2},
            "output": "axe",
            "output_quantity": 1,
        },
        "tapper": {
            "name": "Tapper",
            "ingredients": {"logs": 2, "iron_ingot": 1},
            "output": "tapper",
            "output_quantity": 1,
        },
        "red_paint": {
            "name": "Red Paint",
            "ingredients": {"red_baneberry": 5, "sap": 2, "water": 1},
            "output": "red_paint",
            "output_quantity": 1,
        },
        "blue_paint": {
            "name": "Blue Paint",
            "ingredients": {"blueberry": 5, "sap": 2, "water": 1},
            "output": "blue_paint",
            "output_quantity": 1,
        },
        "green_paint": {
            "name": "Green Paint",
            "ingredients": {"grass_strands": 5, "sap": 2, "water": 1},
            "output": "green_paint",
            "output_quantity": 1,
        },
        "bio_string": {
            "name": "Bio String",
            "ingredients": {"grass_strands": 3},
            "output": "bio_string",
            "output_quantity": 1,
        },
    }
    
    def __init__(self):
        self.inventory = Inventory()
    
    def can_craft(self, recipe_name: str, inventory: Inventory) -> bool:
        """Check if recipe can be crafted with current inventory"""
        if recipe_name not in self.RECIPES:
            return False
        
        recipe = self.RECIPES[recipe_name]
        for ingredient, required_count in recipe["ingredients"].items():
            item = Item(ingredient, ItemType.RESOURCE)
            if inventory.get_item_count(item) < required_count:
                return False
        return True
    
    def craft(self, recipe_name: str, inventory: Inventory) -> bool:
        """Craft item if possible, remove ingredients and add output"""
        if not self.can_craft(recipe_name, inventory):
            return False
        
        recipe = self.RECIPES[recipe_name]
        
        # Remove ingredients
        for ingredient, required_count in recipe["ingredients"].items():
            item = Item(ingredient, ItemType.RESOURCE)
            for _ in range(required_count):
                inventory.remove(item)
        
        # Add output
        output_item = Item(recipe["output"], ItemType.RESOURCE)
        for _ in range(recipe["output_quantity"]):
            inventory.insert(output_item)
        
        return True

# ============================================================================
# ENEMY & COMBAT SYSTEM (From ideaboard - Phase 2)
# ============================================================================

class Enemy:
    """Enemy character (wolf, Brock Calligan, etc)"""
    
    def __init__(self, name: str, position: Vector2, health: int = 50):
        self.name = name
        self.position = position
        self.health = health
        self.max_health = health
        self.velocity = Vector2(0, 0)
        self.speed = 80
        self.is_alive = True
        self.aggression_level = 0  # 0 = passive, 1 = chase with axe, 2 = chase with rifle
    
    def take_damage(self, damage: int):
        """Apply damage"""
        self.health -= damage
        if self.health <= 0:
            self.is_alive = False
    
    def chase_player(self, player_pos: Vector2, delta: float):
        """Move toward player"""
        if not self.is_alive:
            return
        
        dx = player_pos.x - self.position.x
        dy = player_pos.y - self.position.y
        
        # Normalize and apply speed
        distance = (dx**2 + dy**2)**0.5
        if distance > 0:
            self.velocity.x = (dx / distance) * self.speed
            self.velocity.y = (dy / distance) * self.speed
        
        # Update position
        self.position.x += self.velocity.x * delta / 1000
        self.position.y += self.velocity.y * delta / 1000

class BrockCalligan(Enemy):
    """Special enemy NPC with aggression levels from ideaboard"""
    
    def __init__(self, position: Vector2 = None):
        super().__init__("Brock Calligan", position or Vector2(600, 400), health=100)
        self.aggression_level = 0  # 0 = passive, 1 = chase with axe, 2 = chase with rifle
        self.attack_damage = 0
    
    def trigger_hostility(self, trigger_type: str):
        """Make Brock hostile based on trigger"""
        if trigger_type == "enter_house":
            self.aggression_level = 1
            self.attack_damage = 999  # Instant kill with axe
        elif trigger_type == "attack_him":
            self.aggression_level = 2
            self.attack_damage = 999  # Instant kill with rifle
    
    def get_speed_multiplier(self) -> float:
        """Brock is slow but dangerous"""
        if self.aggression_level == 1:
            return 0.5  # Slow with axe
        elif self.aggression_level == 2:
            return 1.0  # Faster with rifle
        return 1.0

class Wolf(Enemy):
    """Wolf enemy that appears at night"""
    
    def __init__(self, position: Vector2):
        super().__init__("Wolf", position, health=30)
        self.speed = 100  # Slightly slower than player
    
    def is_nighttime_enemy(self) -> bool:
        """Wolves only appear at night"""
        return True









# ============================================================================
# DAY/NIGHT SYSTEM
# ============================================================================

class DayNightCycle:
    """Manages day/night progression"""
    
    FULL_DAY_SECONDS = 600.0  # Full day in 10 minutes
    HOURS_IN_DAY = 24
    
    def __init__(self):
        self.elapsed_seconds = 0.0
        self.current_hour = 6  # Start at 6 AM
        self.current_day = 1
        self.observers = []
    
    def update(self, delta: float):
        """Update day/night time"""
        self.elapsed_seconds += delta
        
        # 1 hour = FULL_DAY_SECONDS / HOURS_IN_DAY seconds
        hour_duration = self.FULL_DAY_SECONDS / self.HOURS_IN_DAY
        
        while self.elapsed_seconds >= hour_duration:
            self.elapsed_seconds -= hour_duration
            self.current_hour += 1
            
            if self.current_hour >= 24:
                self.current_hour = 0
                self.current_day += 1
                self._notify("new_day")
            
            self._notify("hour_changed", self.current_hour)
    
    def on_change(self, callback: callable):
        """Subscribe to time changes"""
        self.observers.append(callback)
    
    def _notify(self, event: str, *args):
        for observer in self.observers:
            observer(event, *args)
    
    def get_time_string(self) -> str:
        """Get formatted time"""
        return f"Day {self.current_day}, {self.current_hour:02d}:00"
    
    def is_dark(self) -> bool:
        """Check if night time (18:00 - 6:00)"""
        return self.current_hour >= 18 or self.current_hour < 6

# ============================================================================
# NPC & DIALOGUE SYSTEM
# ============================================================================

class QuestTracker:
    """Track quest progress and story events"""
    
    def __init__(self):
        # Quest stages from storyline
        self.stage = 0  # 0 = not started, 1 = Zea's quest, 2 = Mt. Crag, etc.
        self.quest_active = False
        self.quest_name = "None"
        self.quest_progress = {}
        
        # Zea's initial quest requirements
        self.quest_requirements = {
            1: {  # Zea's quest
                "pinecones": (200, 0),  # (required, collected)
                "sticks": (5000, 0),
                "sorrel": (50, 0),
                "red_baneberries": (10000, 0),
                "chives": (100, 0),
                "elderberries": (100, 0),
            }
        }
        
        # Story dialogue progression
        self.dialogue_stage = 0
        self.met_zea = False
        self.explored_town = False
        self.visited_mt_crag = False
        self.has_farm_contract = False
        self.starting_money = 100
    
    def start_quest(self, quest_id: int):
        """Activate a quest"""
        if quest_id in self.quest_requirements:
            self.stage = quest_id
            self.quest_active = True
            if quest_id == 1:
                self.quest_name = "Help Zea's Mother"
                self.quest_progress = self.quest_requirements[quest_id].copy()
    
    def add_quest_item(self, item_name: str, count: int = 1):
        """Track item collected for quest"""
        if self.stage in self.quest_requirements and item_name in self.quest_requirements[self.stage]:
            required, collected = self.quest_requirements[self.stage][item_name]
            self.quest_requirements[self.stage][item_name] = (required, collected + count)
            return collected + count >= required
        return False
    
    def is_quest_complete(self) -> bool:
        """Check if current quest is complete"""
        if self.stage not in self.quest_requirements:
            return False
        
        for item_name, (required, collected) in self.quest_requirements[self.stage].items():
            if collected < required:
                return False
        return True
    
    def get_quest_status(self) -> str:
        """Get human-readable quest status"""
        if not self.quest_active:
            return "No active quest"
        
        status = f"{self.quest_name}:\n"
        if self.stage in self.quest_requirements:
            for item, (required, collected) in self.quest_requirements[self.stage].items():
                status += f"  {item}: {collected}/{required}\n"
        return status

class DialogueSystem:
    """NPC dialogue and trading"""
    
    # NPCs from game with extended dialogue
    NPCS = {
        "zea": NPCData(
            name="Zea",
            position=Vector2(100, 200),
            dialogue_lines=[
                "A new person? We never get those here.",
                "Welcome to Shelburne, New Hampshire.",
                "The best forms of jobs you will find here are farms.",
                "I recon you could start your own one. I can fund you, if...",
                "I need some items... my mom needs them... she isn't feeling well.",
                "Tears start to fall from her eyes.",
                "You know what to do.",
                "Meet us at Mt. Crag when you're done.",
            ]
        ),
        "leo": NPCData(
            name="Leo Dune",
            position=Vector2(400, 300),
            dialogue_lines=[
                "Welcome to my shop!",
                "We have fine spirits here.",
                "You have proven yourself very helpful.",
                "Not much people can manage such a requiring task.",
                "We are all here astonished by your persistence.",
            ],
            location_zone="shelburne"
        ),
        "philip": NPCData(
            name="Philip",
            position=Vector2(350, 350),
            dialogue_lines=[
                "Hi, let me introduce myself. My name is Philip.",
                "I'm amazed by your dedication to be a farmer.",
                "I will grant you a 10% discount on all farmer-related items.",
                "That's seeds and tools.",
            ],
            location_zone="shelburne"
        ),
        "brock_calligan": NPCData(
            name="Brock Calligan",
            position=Vector2(600, 400),
            dialogue_lines=[
                "Stay out of my way.",
                "This town is mine.",
            ],
            location_zone="shelburne",
            quest_stage=0
        ),
        "michael_view": NPCData(
            name="Michael View",
            position=Vector2(500, 400),
            dialogue_lines=[
                "This is my farm now.",
            ],
            location_zone="world_2",
            quest_stage=0
        ),
    }
    
    def __init__(self):
        self.npcs = {name: npc for name, npc in self.NPCS.items()}
        self.current_dialogue = None
        self.dialogue_index = 0
    
    def talk_to_npc(self, npc_name: str) -> str:
        """Get next dialogue line from NPC"""
        if npc_name not in self.npcs:
            return "..."
        
        npc = self.npcs[npc_name]
        if self.dialogue_index >= len(npc.dialogue_lines):
            self.dialogue_index = 0
        
        line = npc.dialogue_lines[self.dialogue_index]
        self.dialogue_index += 1
        return line
    
    def get_npc_position(self, npc_name: str) -> Optional[Vector2]:
        """Get NPC location"""
        if npc_name in self.npcs:
            return self.npcs[npc_name].position
        return None

# ============================================================================
# PLAYER SYSTEM (From unique_player.gd)
# ============================================================================

class Player:
    """Player character with movement and animation"""
    
    SPEED = 100
    SPRINT_SPEED = 200
    
    # Animation states matching GD script
    ANIMATIONS = {
        Direction.DOWN: ("walk_down", "walk_down_idle"),
        Direction.UP: ("walk_up", "walk_up_idle"),
        Direction.LEFT: ("walk_left", "walk_left_idle"),
        Direction.RIGHT: ("walk_left", "walk_left_idle"),  # Right uses left sprite flipped
    }
    
    def __init__(self, position: Vector2):
        self.position = position
        self.velocity = Vector2(0, 0)
        self.current_direction = Direction.NONE
        self.is_moving = False
        self.current_animation = "walk_down_idle"
        self.inventory = Inventory()
        self.camera_position = Vector2(0, 0)
    
    def handle_input(self):
        """Process player input (would be called from game loop)"""
        dx = 0
        dy = 0
        
        # Arrow keys or WASD
        if tk.Key.Up in current_keys or 'w' in current_keys:
            self.current_direction = Direction.UP
            dy = -1
        elif tk.Key.Down in current_keys or 's' in current_keys:
            self.current_direction = Direction.DOWN
            dy = 1
        elif tk.Key.Left in current_keys or 'a' in current_keys:
            self.current_direction = Direction.LEFT
            dx = -1
        elif tk.Key.Right in current_keys or 'd' in current_keys:
            self.current_direction = Direction.RIGHT
            dx = 1
        
        # Sprint (SHIFT)
        speed = self.SPRINT_SPEED if 'Shift_L' in current_keys else self.SPEED
        
        self.velocity = Vector2(dx * speed, dy * speed)
        self.is_moving = (dx != 0 or dy != 0)
        self._update_animation()
    
    def _update_animation(self):
        """Update current animation based on state"""
        if self.current_direction not in self.ANIMATIONS:
            return
        
        walk_anim, idle_anim = self.ANIMATIONS[self.current_direction]
        self.current_animation = walk_anim if self.is_moving else idle_anim
    
    def update(self, delta: float):
        """Update player position and animation"""
        self.position += Vector2(self.velocity.x * delta / 1000, self.velocity.y * delta / 1000)
        self.camera_position = self.position  # Follow player
    
    def collect_item(self, item: Item):
        """Collect item into inventory"""
        self.inventory.insert(item)
    
    def consume_alcohol(self, alcohol_item: Item, drunkenness_system: 'DrunkennessSystem'):
        """Consume alcohol from inventory if available"""
        if self.inventory.get_item_count(alcohol_item) > 0:
            # Map item names to DRPS values
            drps_map = {
                "Beer": 15,
                "Mead": 15,
                "Hunter's Liquor": 50,
                "Red Wine": 5,
                "Vodka": 85,
                "Whiskey": 75,
            }
            drps = drps_map.get(alcohol_item.name, 10)
            drunkenness_system.consume_alcohol(drps)
            self.inventory.remove(alcohol_item)
            return True
        return False

# ============================================================================
# ZONE/SCENE MANAGEMENT (From TSCN files)
# ============================================================================

class ZoneManager:
    """Manages zone transitions and scene loading"""
    
    ZONES = {
        "world_2": ZoneData(
            name="World 2",
            tilemap_width=100,
            tilemap_height=100,
            spawn_position=Vector2(500, 400),
            zone_transitions={
                "shelburne": Vector2(600, 300),
            }
        ),
        "shelburne": ZoneData(
            name="Shelburne",
            tilemap_width=200,
            tilemap_height=150,
            spawn_position=Vector2(100, 100),
            zone_transitions={
                "world_2": Vector2(600, 300),
                "zea_house": Vector2(700, 500),
                "leo_shop": Vector2(400, 400),
            }
        ),
        "cave": ZoneData(
            name="Cave",
            tilemap_width=80,
            tilemap_height=80,
            spawn_position=Vector2(40, 40),
            zone_transitions={
                "shelburne": Vector2(0, 0),
            }
        ),
    }
    
    def __init__(self, asset_manager: AssetManager):
        self.current_zone = "world_2"
        self.zones_loaded = {}
        self.asset_manager = asset_manager
        self.dialogue_system = DialogueSystem()
    
    def load_zone(self, zone_name: str) -> ZoneData:
        """Load zone data"""
        if zone_name in self.zones_loaded:
            return self.zones_loaded[zone_name]
        
        if zone_name not in self.ZONES:
            print(f"Zone {zone_name} not found")
            return None
        
        zone = self.ZONES[zone_name]
        self.zones_loaded[zone_name] = zone
        return zone
    
    def transition_to_zone(self, zone_name: str, entry_position: Optional[Vector2] = None) -> Vector2:
        """Transition to new zone, return spawn position"""
        self.current_zone = zone_name
        zone = self.load_zone(zone_name)
        
        if entry_position:
            return entry_position
        return zone.spawn_position

# ============================================================================
# MAIN GAME ENGINE
# ============================================================================

class CroptopiaGame:
    """Main game engine"""
    
    def __init__(self, root_frame):
        self.root_frame = root_frame
        self.running = True
        self.clock_time = 0
        
        # Initialize systems
        self.asset_manager = AssetManager(ASSETS_PATH)
        self.zone_manager = ZoneManager(self.asset_manager)
        self.player = Player(Vector2(500, 400))
        self.crop_system = CropSystem()
        self.economy_manager = EconomyManager()
        self.day_night = DayNightCycle()
        
        # New systems
        self.quest_tracker = QuestTracker()
        self.drunkenness = DrunkennessSystem()
        self.luck = LuckSystem()
        self.crafting = CraftingSystem()
        self.item_database = ItemDatabase()
        
        # Enemy system
        self.enemies = []
        self.brock_calligan = BrockCalligan(Vector2(600, 400))
        self.enemies.append(self.brock_calligan)
        
        # Story initialization
        self.show_title_screen = True
        self.dialogue_text = ""
        self.dialogue_timer = 0
        
        # UI
        self.canvas = TkCanvas(
            root_frame,
            width=WINDOW_WIDTH,
            height=WINDOW_HEIGHT,
            bg="#2a2a2a",
            highlightthickness=0
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Bind events only to this canvas, not globally
        self.canvas.bind('<Key>', self._on_key_down)
        self.canvas.bind('<KeyRelease>', self._on_key_up)
        self.canvas.focus_set()  # Give canvas focus so it receives key events
        
        self.keys_pressed = set()
        
        # Game state
        self.frame_count = 0
        self.fps_counter = 0
        self.last_time = time.time()
    
    def _on_key_down(self, event):
        """Key press handler"""
        self.keys_pressed.add(event.keysym)
    
    def _on_key_up(self, event):
        """Key release handler"""
        self.keys_pressed.discard(event.keysym)
    
    def update(self, delta: float):
        """Update game logic"""
        # Player
        self._handle_player_input()
        self.player.update(delta)
        
        # Crops
        self.crop_system.update(delta)
        
        # Time
        self.day_night.update(delta)
        
        # Drunkenness (sober up over time)
        if self.drunkenness.drps > 0:
            self.drunkenness.sober_up(delta / 1000)  # Convert ms to seconds
        
        # Update enemies
        for enemy in self.enemies:
            if enemy.is_alive:
                if enemy.aggression_level > 0:
                    enemy.chase_player(self.player.position, delta)
        
        # Spawn wolves at night
        if self.day_night.is_dark() and len([e for e in self.enemies if isinstance(e, Wolf)]) < 3:
            # Spawn wolf at random location away from player
            wolf_x = random.randint(100, WINDOW_WIDTH - 100)
            wolf_y = random.randint(100, WINDOW_HEIGHT - 100)
            wolf = Wolf(Vector2(wolf_x, wolf_y))
            self.enemies.append(wolf)
        
        # Remove dead enemies
        self.enemies = [e for e in self.enemies if e.is_alive or not isinstance(e, Wolf)]
        
        # Dialogue display timeout
        if self.dialogue_text:
            self.dialogue_timer -= delta
            if self.dialogue_timer <= 0:
                self.dialogue_text = ""
    
    def _handle_player_input(self):
        """Handle player input from keys_pressed"""
        # This would integrate with player.handle_input()
        pass
    
    def render(self):
        """Render game to canvas"""
        self.canvas.delete("all")
        
        # Get current zone
        zone = self.zone_manager.zones_loaded.get(
            self.zone_manager.current_zone,
            self.zone_manager.load_zone(self.zone_manager.current_zone)
        )
        
        if not zone:
            return
        
        # Draw background (green grass placeholder)
        self.canvas.create_rectangle(
            0, 0,
            WINDOW_WIDTH, WINDOW_HEIGHT,
            fill="#2d5a2d"
        )
        
        # Draw grid (tilemap visual)
        tile_size = 32
        for x in range(0, WINDOW_WIDTH, tile_size):
            self.canvas.create_line(x, 0, x, WINDOW_HEIGHT, fill="#1a3a1a", width=1)
        for y in range(0, WINDOW_HEIGHT, tile_size):
            self.canvas.create_line(0, y, WINDOW_WIDTH, y, fill="#1a3a1a", width=1)
        
        # Draw player
        self.canvas.create_oval(
            self.player.position.x - 16,
            self.player.position.y - 16,
            self.player.position.x + 16,
            self.player.position.y + 16,
            fill="blue", outline="white", width=2
        )
        
        # Draw enemies
        for enemy in self.enemies:
            if enemy.is_alive:
                if isinstance(enemy, BrockCalligan):
                    color = "red" if enemy.aggression_level > 0 else "darkred"
                elif isinstance(enemy, Wolf):
                    color = "gray"
                else:
                    color = "orange"
                
                self.canvas.create_oval(
                    enemy.position.x - 12,
                    enemy.position.y - 12,
                    enemy.position.x + 12,
                    enemy.position.y + 12,
                    fill=color, outline="white", width=1
                )
                
                # Draw health bar for Brock
                if isinstance(enemy, BrockCalligan) and enemy.health < enemy.max_health:
                    bar_width = 24
                    bar_height = 4
                    health_ratio = enemy.health / enemy.max_health
                    self.canvas.create_rectangle(
                        enemy.position.x - bar_width // 2,
                        enemy.position.y - 20,
                        enemy.position.x + bar_width // 2,
                        enemy.position.y - 16,
                        fill="darkred", outline="white"
                    )
                    self.canvas.create_rectangle(
                        enemy.position.x - bar_width // 2,
                        enemy.position.y - 20,
                        enemy.position.x - bar_width // 2 + (bar_width * health_ratio),
                        enemy.position.y - 16,
                        fill="red", outline="white"
                    )
        
        # Draw HUD
        self._draw_hud(zone)
    
    def _draw_hud(self, zone: ZoneData):
        """Draw UI elements"""
        # Time display
        time_text = self.day_night.get_time_string()
        if self.day_night.is_dark():
            time_text += " [NIGHT]"
        self.canvas.create_text(
            10, 10,
            text=time_text,
            fill="white",
            anchor="nw",
            font=("Arial", 12, "bold")
        )
        
        # Zone name
        self.canvas.create_text(
            WINDOW_WIDTH // 2, 10,
            text=f"Zone: {zone.name}",
            fill="white",
            anchor="n",
            font=("Arial", 14, "bold")
        )
        
        # Inventory count
        inventory_text = f"Inventory: {len(self.player.inventory.items)}/{self.player.inventory.max_slots}"
        self.canvas.create_text(
            WINDOW_WIDTH - 10, 10,
            text=inventory_text,
            fill="white",
            anchor="ne",
            font=("Arial", 12)
        )
        
        # Quest status
        if self.quest_tracker.quest_active:
            quest_status = self.quest_tracker.get_quest_status()
            self.canvas.create_text(
                10, 40,
                text=quest_status,
                fill="#ffdd00",
                anchor="nw",
                font=("Arial", 10),
                justify="left"
            )
        
        # Drunkenness status
        if self.drunkenness.drps > 0:
            drps_text = f"DRPS: {self.drunkenness.drps}/{self.drunkenness.MAX_DRPS}"
            color = "#ff3333" if self.drunkenness.is_drunk else "#ffaa00"
            self.canvas.create_text(
                10, WINDOW_HEIGHT - 80,
                text=drps_text,
                fill=color,
                anchor="nw",
                font=("Arial", 11, "bold")
            )
        
        # Luck points
        if self.luck.luck_points > 0:
            luck_text = f"Luck: {self.luck.luck_points}"
            self.canvas.create_text(
                10, WINDOW_HEIGHT - 60,
                text=luck_text,
                fill="#ffff00",
                anchor="nw",
                font=("Arial", 11, "bold")
            )
        
        # Enemy count
        alive_enemies = [e for e in self.enemies if e.is_alive]
        if alive_enemies:
            enemy_text = f"Enemies: {len(alive_enemies)}"
            self.canvas.create_text(
                WINDOW_WIDTH - 10, WINDOW_HEIGHT - 60,
                text=enemy_text,
                fill="#ff0000",
                anchor="ne",
                font=("Arial", 11, "bold")
            )
        
        # Nighttime warning
        if self.day_night.is_dark():
            self.canvas.create_text(
                WINDOW_WIDTH // 2, WINDOW_HEIGHT - 40,
                text="⚠ BEWARE: ENEMIES ACTIVE AT NIGHT ⚠",
                fill="#ff3333",
                anchor="s",
                font=("Arial", 12, "bold")
            )
        
        # Dialogue display
        if self.dialogue_text:
            # Draw dialogue box
            box_height = 100
            self.canvas.create_rectangle(
                50, WINDOW_HEIGHT - box_height - 20,
                WINDOW_WIDTH - 50, WINDOW_HEIGHT - 20,
                fill="#1a1a1a", outline="white", width=2
            )
            self.canvas.create_text(
                60, WINDOW_HEIGHT - box_height,
                text=self.dialogue_text,
                fill="white",
                anchor="nw",
                font=("Arial", 11),
                width=WINDOW_WIDTH - 120,
                justify="left"
            )
        
        # FPS
        self.canvas.create_text(
            10, WINDOW_HEIGHT - 20,
            text=f"FPS: {self.fps_counter}",
            fill="#666666",
            anchor="sw",
            font=("Arial", 10)
        )
    
    def run(self):
        """Main game loop"""
        def game_loop():
            if not self.running:
                return  # Don't schedule next loop if stopped
            
            try:
                try:
                    if not self.root_frame.winfo_exists():
                        self.running = False
                        return
                except Exception:
                    self.running = False
                    return

                current_time = time.time()
                delta = min((current_time - self.last_time) * 1000, 50)  # Cap at 50ms
                self.last_time = current_time
                
                self.update(delta)
                self.render()
                
                # FPS counter
                self.frame_count += 1
                if time.time() - self.last_time > 1.0:
                    self.fps_counter = self.frame_count
                    self.frame_count = 0
                
                # Schedule next loop only if still running
                if self.running:
                    try:
                        self.root_frame.after(int(1000 / FPS), game_loop)
                    except Exception:
                        self.running = False
            except Exception as e:
                # Log errors but don't crash
                print(f"Game loop error: {e}")
                if self.running:
                    try:
                        self.root_frame.after(int(1000 / FPS), game_loop)
                    except Exception:
                        self.running = False
        
        game_loop()
    
    def stop(self):
        """Stop the game"""
        self.running = False

# ============================================================================
# WINDOW INTEGRATION FOR DOUBOS
# ============================================================================

class RootProxy:
    """Proxy for tk.Tk interface compatibility"""
    def __init__(self, frame):
        self.frame = frame
        self.tk = frame.winfo_toplevel().tk  # Get the actual Tk instance
    
    def title(self, text):
        pass
    
    def geometry(self, geom):
        pass
    
    def resizable(self, width, height):
        pass
    
    def after(self, ms, func):
        """Schedule a callback - use frame's after directly"""
        return self.frame.after(ms, func)
    
    def after_cancel(self, callback_id):
        """Cancel a scheduled callback"""
        try:
            self.frame.after_cancel(callback_id)
        except:
            pass
    
    def bind(self, key, func):
        """Bind event - use frame's bind directly"""
        return self.frame.bind(key, func)
    
    def call(self, *args):
        """Proxy for tk.call - delegate to actual Tk instance"""
        if hasattr(self, 'tk') and self.tk:
            try:
                return self.tk.call(*args)
            except:
                return None
        return None
    
    def __getattr__(self, name):
        """Fallback for other attributes - try to delegate to frame or tk"""
        if hasattr(self.frame, name):
            return getattr(self.frame, name)
        if hasattr(self.tk, name):
            return getattr(self.tk, name)
        return None

class CroptopiaGameWindow(tk.Frame):
    """Croptopia game embedded in DoubOS window"""
    
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        
        # Create game
        self.game = CroptopiaGame(self)
        
        # Proxy for compatibility
        self.root_proxy = RootProxy(self)
        self.title = self.root_proxy.title
        self.geometry = self.root_proxy.geometry
        self.resizable = self.root_proxy.resizable
        
        # Bind destroy event to stop game properly (use parent class method directly)
        super().bind('<Destroy>', self._on_destroy)
        
        # Schedule game loop to start after initialization
        super().after(100, self.game.run)
    
    def _on_destroy(self, event=None):
        """Clean up when window closes"""
        try:
            self.game.stop()
        except:
            pass  # Silently fail if already stopped
    
    def on_destroy(self):
        """Clean up when window closes (alternative interface)"""
        self._on_destroy()

# For backward compatibility
UltimatecroptopiaGame = CroptopiaGameWindow

if __name__ == "__main__":
    # Test standalone
    root = tk.Tk()
    root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
    root.title("Croptopia - Standalone Test")
    
    game_window = CroptopiaGameWindow(root)
    game_window.pack(fill=tk.BOTH, expand=True)
    
    root.mainloop()
    root.mainloop()
