#!/usr/bin/env python3
"""
CROPTOPIA - NATIVE PYTHON ENGINE (1:1 RECREATION)
==================================================
Exact recreation matching the visual style from screenshots.
Uses Pygame for high-fidelity pixel-perfect rendering.
"""

import pygame
import sys
import json
import math
import random
from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional
from pathlib import Path
from collections import defaultdict
import re

# ============================================================================
# CONSTANTS - EXACT PIXEL DIMENSIONS FROM SCREENSHOTS
# ============================================================================

# Screen
SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080
FPS = 60

# Tile system (from actual assets)
TILE_SIZE = 48  # grass_2.png is 48x48
WORLD_TILES_X = 100
WORLD_TILES_Y = 100

# Asset paths (Godot project)
ASSET_ROOT = Path(__file__).parent / "Croptopia - 02.11.25"
ASSET_DIR = ASSET_ROOT / "assets"
ASSET_ITEMS_DIR = ASSET_DIR / "Item Assets"
ASSET_CROPS_DIR = ASSET_ITEMS_DIR / "Crops"
ASSET_INVENTORY_DIR = ASSET_ROOT / "inventory"

# Colors (extracted from screenshots)
COLOR_GRASS = (93, 214, 93)         # Bright grass green
COLOR_GRASS_DARK = (60, 180, 60)    # Darker grass for variation
COLOR_FOREST_GREEN = (44, 160, 44)  # Forest green
COLOR_DARK_BG = (20, 20, 20)        # Dark UI background
COLOR_WOOD = (139, 101, 65)         # Brown wood
COLOR_WOOD_LIGHT = (180, 140, 80)   # Light tan wood
COLOR_WOOD_BORDER = (100, 70, 40)   # Dark wood border
COLOR_TEXT_DARK = (0, 0, 0)         # Black text
COLOR_TEXT_LIGHT = (240, 240, 240)  # White text
COLOR_ACCENT_ORANGE = (255, 165, 0) # Orange UI accent
COLOR_ACCENT_BLUE = (100, 150, 200) # Blue accent

# UI dimensions (from assets)
INVENTORY_SLOT_SIZE = TILE_SIZE
INVENTORY_SLOTS = 8
SHOP_GRID_COLS = 5
SHOP_GRID_ROWS = 5
SHOP_ITEM_SIZE = TILE_SIZE

# Timing
GAME_TIME_SCALE = 0.1  # 1 real second = 0.1 game minutes
FRAME_RATE = FPS

# ============================================================================
# ENUMS
# ============================================================================

class Direction(Enum):
    """8 directions."""
    NONE = (0, 0)
    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)
    UP_LEFT = (-1, -1)
    UP_RIGHT = (1, -1)
    DOWN_LEFT = (-1, 1)
    DOWN_RIGHT = (1, 1)

class GameState(Enum):
    """Game modes."""
    WORLD = "world"
    SHOP = "shop"
    INVENTORY = "inventory"
    DIALOGUE = "dialogue"
    PAUSED = "paused"

class ItemType(Enum):
    """Item categories."""
    TOOL = "tool"
    SEED = "seed"
    CROP = "crop"
    RESOURCE = "resource"
    BUILDING = "building"

# ============================================================================
# DATA CLASSES
# ============================================================================

@dataclass
class Item:
    """Game item."""
    name: str
    item_type: ItemType
    stack_size: int = 1
    max_stack: int = 99
    value: int = 0  # Sell price
    image_key: str = ""
    
    def add(self, amount: int = 1) -> bool:
        """Add to stack."""
        if self.stack_size + amount <= self.max_stack:
            self.stack_size += amount
            return True
        return False

@dataclass
class Sprite:
    """Sprite for rendering."""
    image: pygame.Surface
    rect: pygame.Rect
    visible: bool = True
    z_index: int = 0

@dataclass
class Entity:
    """Game entity (player, NPC, etc)."""
    name: str
    x: float
    y: float
    width: int = TILE_SIZE
    height: int = TILE_SIZE
    velocity_x: float = 0.0
    velocity_y: float = 0.0
    speed: float = 100.0  # pixels per second
    direction: Direction = Direction.NONE
    sprite: Optional[Sprite] = None

# ============================================================================
# ASSET MANAGER
# ============================================================================

class AssetManager:
    """Load and cache Croptopia assets from the Godot project."""

    def __init__(self):
        self.cache: Dict[Tuple[str, Optional[Tuple[int, int]]], pygame.Surface] = {}
        self.grass_tiles: List[pygame.Surface] = []
        self.tree_sprites: List[pygame.Surface] = []
        self.player_frames: List[pygame.Surface] = []
        self.ui: Dict[str, pygame.Surface] = {}
        self.item_images: Dict[str, pygame.Surface] = {}
        self._load_assets()

    def _load_image(self, path: Path, scale: Optional[Tuple[int, int]] = None) -> Optional[pygame.Surface]:
        if not path.exists():
            return None
        key = (str(path), scale)
        if key in self.cache:
            return self.cache[key]
        image = pygame.image.load(str(path)).convert_alpha()
        if scale:
            image = pygame.transform.scale(image, scale)
        self.cache[key] = image
        return image

    def _load_assets(self):
        # Grass tiles
        for name in ["grass_2.png", "grass_3.png"]:
            tile = self._load_image(ASSET_DIR / name, (TILE_SIZE, TILE_SIZE))
            if tile:
                self.grass_tiles.append(tile)

        # Trees
        for name in ["maple_tree.png", "birch_tree.png", "sweet_gum_tree.png", "spruce.png", "white_pine.png"]:
            tree = self._load_image(ASSET_DIR / name)
            if tree:
                self.tree_sprites.append(tree)

        # Player frames
        sheet = self._load_image(ASSET_DIR / "michael_full_walk_cycle.png")
        if sheet:
            frame_w = sheet.get_width() // 8
            frame_h = sheet.get_height()
            for i in range(8):
                frame = sheet.subsurface(pygame.Rect(i * frame_w, 0, frame_w, frame_h))
                frame = pygame.transform.scale(frame, (TILE_SIZE, TILE_SIZE))
                self.player_frames.append(frame)

        # UI assets
        self.ui["hotbar"] = self._load_image(ASSET_DIR / "hotbar_asset.png")
        self.ui["ui_bg"] = self._load_image(ASSET_DIR / "ui_bg.png")
        self.ui["ui_bar"] = self._load_image(ASSET_DIR / "ui_bar.png")
        self.ui["level_frame"] = self._load_image(ASSET_DIR / "level_frame.png")

        # World tiles
        path_tile = self._load_image(ASSET_DIR / "path_9x9.png", (TILE_SIZE, TILE_SIZE))
        road_tile = self._load_image(ASSET_DIR / "main_road_curve.png", (TILE_SIZE, TILE_SIZE))
        water_sheet = self._load_image(ASSET_DIR / "water_tiles_2.png")
        water_tile = None
        if water_sheet:
            water_tile = pygame.transform.scale(water_sheet.subsurface(pygame.Rect(0, 0, 48, 48)), (TILE_SIZE, TILE_SIZE))

        self.ui["path_tile"] = path_tile
        self.ui["road_tile"] = road_tile
        self.ui["water_tile"] = water_tile

        # Item images
        self.item_images["axe"] = self._load_image(ASSET_DIR / "iron_axe.png", (TILE_SIZE, TILE_SIZE))
        self.item_images["pickaxe"] = self._load_image(ASSET_DIR / "iron_pickaxe.png", (TILE_SIZE, TILE_SIZE))
        self.item_images["seed_packet"] = self._load_image(ASSET_DIR / "seed_packet_neutral.png", (TILE_SIZE, TILE_SIZE))
        self.item_images["pouch"] = self._load_image(ASSET_DIR / "pouch.png", (TILE_SIZE, TILE_SIZE))
        self.item_images["birch_log"] = self._load_image(ASSET_ITEMS_DIR / "birch_log.png", (TILE_SIZE, TILE_SIZE))
        self.item_images["oak_log"] = self._load_image(ASSET_ITEMS_DIR / "oak_log.png", (TILE_SIZE, TILE_SIZE))
        self.item_images["spruce_log"] = self._load_image(ASSET_ITEMS_DIR / "spruce_log.png", (TILE_SIZE, TILE_SIZE))
        self.item_images["elderberry_log"] = self._load_image(ASSET_ITEMS_DIR / "elderberry_log.png", (TILE_SIZE, TILE_SIZE))

        crop_sheet = self._load_image(ASSET_CROPS_DIR / "crop_array_0.0.png")
        if crop_sheet:
            crop_frame = crop_sheet.subsurface(pygame.Rect(0, 0, 32, 32))
            crop_frame = pygame.transform.scale(crop_frame, (TILE_SIZE, TILE_SIZE))
            self.item_images["crop_sheet"] = crop_frame

# ============================================================================
# WORLD & TILEMAP
# ============================================================================

@dataclass
class TileCell:
    x: int
    y: int
    tile_id: int
    alt: int


class SceneLayer:
    def __init__(self, index: int):
        self.index = index
        self.cells: List[TileCell] = []


class World2Scene:
    """World 2 scene loaded from Godot .tscn tile data."""

    def __init__(self, asset_manager: AssetManager):
        self.assets = asset_manager
        self.layers: Dict[int, SceneLayer] = {}
        self.tilemap_offset = (-159, -177)  # world2main + TileMap offsets
        self._load_world2()

    @staticmethod
    def _decode_coord(packed: int) -> Tuple[int, int]:
        x = packed & 0xFFFF
        y = (packed >> 16) & 0xFFFF
        if x >= 32768:
            x -= 65536
        if y >= 32768:
            y -= 65536
        return x, y

    def _load_world2(self):
        path = ASSET_ROOT / "world_2.tscn"
        if not path.exists():
            return
        text = path.read_text(encoding="utf-8")

        for m in re.finditer(r"layer_(\d+)/tile_data = PackedInt32Array\((.*?)\)", text, re.S):
            layer_idx = int(m.group(1))
            arr = m.group(2).strip()
            if not arr:
                continue
            ints = [int(x) for x in re.split(r"\s*,\s*", arr) if x != ""]

            layer = SceneLayer(layer_idx)
            for i in range(0, len(ints), 3):
                if i + 2 >= len(ints):
                    break
                packed = ints[i]
                tile_id = ints[i + 1]
                alt = ints[i + 2]
                x, y = self._decode_coord(packed)
                layer.cells.append(TileCell(x, y, tile_id, alt))
            self.layers[layer_idx] = layer

    def _get_layer_texture(self, layer_idx: int, tile_id: int) -> Optional[pygame.Surface]:
        if layer_idx == 0:
            if self.assets.grass_tiles:
                return self.assets.grass_tiles[tile_id % len(self.assets.grass_tiles)]
        elif layer_idx == 1:
            if self.assets.tree_sprites:
                return self.assets.tree_sprites[tile_id % len(self.assets.tree_sprites)]
        elif layer_idx == 2:
            return self.assets.ui.get("path_tile")
        elif layer_idx == 3:
            return self.assets.ui.get("road_tile")
        elif layer_idx == 4:
            return self.assets.ui.get("water_tile")
        return None

    def render(self, surface: pygame.Surface, camera_x: float, camera_y: float):
        for layer_idx in sorted(self.layers.keys()):
            layer = self.layers[layer_idx]
            for cell in layer.cells:
                tex = self._get_layer_texture(layer_idx, cell.tile_id)
                if not tex:
                    continue
                screen_x = (cell.x * TILE_SIZE) - camera_x + self.tilemap_offset[0]
                screen_y = (cell.y * TILE_SIZE) - camera_y + self.tilemap_offset[1]

                if layer_idx == 1 and tex.get_height() > TILE_SIZE:
                    screen_x -= max(0, tex.get_width() - TILE_SIZE) // 2
                    screen_y -= max(0, tex.get_height() - TILE_SIZE)

                surface.blit(tex, (screen_x, screen_y))

class TileMap:
    """Grid-based tilemap."""
    
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.tiles: List[List[str]] = [["grass"] * width for _ in range(height)]
        self._generate_world()
    
    def _generate_world(self):
        """Generate initial world layout with forest pattern."""
        # Start with grass
        for y in range(self.height):
            for x in range(self.width):
                self.tiles[y][x] = "grass"
        
        # Generate forest clusters (matching screenshot)
        forest_centers = [
            (30, 20), (50, 35), (70, 25), (85, 40),
            (25, 50), (45, 55), (65, 45), (80, 60),
            (35, 70), (55, 75), (70, 70),
        ]
        
        # Draw forest around centers with density
        for cx, cy in forest_centers:
            for x in range(cx - 15, cx + 15):
                for y in range(cy - 15, cy + 15):
                    if 0 <= x < self.width and 0 <= y < self.height:
                        # Circular forest with falloff
                        dist = math.sqrt((x - cx)**2 + (y - cy)**2)
                        if dist < 12:
                            if random.random() < 0.7:
                                self.tiles[y][x] = "forest"
                        elif dist < 15:
                            if random.random() < 0.3:
                                self.tiles[y][x] = "forest"
        
        # Add clearings for buildings
        self.tiles[25][30] = "grass"
        self.tiles[25][31] = "grass"
        self.tiles[26][30] = "grass"
        self.tiles[26][31] = "grass"
    
    def get_tile(self, x: int, y: int) -> str:
        """Get tile type."""
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.tiles[y][x]
        return "grass"
    
    def set_tile(self, x: int, y: int, tile_type: str):
        """Set tile type."""
        if 0 <= x < self.width and 0 <= y < self.height:
            self.tiles[y][x] = tile_type

# ============================================================================
# PLAYER
# ============================================================================

class Player(Entity):
    """Player character."""
    
    def __init__(self, asset_manager: AssetManager, x: float = 500, y: float = 500):
        super().__init__("Michael", x, y)
        self.inventory: List[Optional[Item]] = [None] * INVENTORY_SLOTS
        self.selected_slot = 0
        self.facing_direction = Direction.DOWN
        self.animation_timer = 0.0
        self.animation_frame = 0
        self.animation_speed = 0.12
        self.frames = asset_manager.player_frames if asset_manager.player_frames else []
        
        # Create initial sprite
        base_frame = self.frames[0] if self.frames else pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
        self.sprite = Sprite(
            image=base_frame,
            rect=pygame.Rect(0, 0, TILE_SIZE, TILE_SIZE)
        )
        
        # Add starter items
        self.inventory[0] = Item("Axe", ItemType.TOOL, 1, image_key="axe")
        self.inventory[1] = Item("Seed Packet", ItemType.SEED, 5, image_key="seed_packet")
    
    def update(self, delta_time: float):
        """Update player."""
        moving = self.velocity_x != 0 or self.velocity_y != 0

        if moving:
            self.x += self.velocity_x * delta_time
            self.y += self.velocity_y * delta_time

            # Clamp to world
            self.x = max(0, min(self.x, WORLD_TILES_X * TILE_SIZE - TILE_SIZE))
            self.y = max(0, min(self.y, WORLD_TILES_Y * TILE_SIZE - TILE_SIZE))

        # Animate
        if self.frames:
            if moving:
                self.animation_timer += delta_time
                if self.animation_timer >= self.animation_speed:
                    self.animation_timer = 0.0
                    self.animation_frame = (self.animation_frame + 1) % len(self.frames)
            else:
                self.animation_frame = 0

            self.sprite.image = self.frames[self.animation_frame]
    
    def add_item(self, item: Item) -> bool:
        """Add item to inventory."""
        # Try to stack
        for slot in self.inventory:
            if slot and slot.name == item.name and slot.add(item.stack_size):
                return True
        
        # Find empty slot
        for i, slot in enumerate(self.inventory):
            if slot is None:
                self.inventory[i] = item
                return True
        
        return False  # Inventory full
    
    def get_selected_item(self) -> Optional[Item]:
        """Get currently selected item."""
        return self.inventory[self.selected_slot]

# ============================================================================
# GAME WORLD
# ============================================================================

class GameWorld:
    """Game world container."""
    
    def __init__(self):
        self.assets = AssetManager()
        self.tilemap = TileMap(WORLD_TILES_X, WORLD_TILES_Y)
        self.player = Player(self.assets)
        self.entities: List[Entity] = [self.player]
        self.sprite_cache: Dict[str, pygame.Surface] = {}
        self.tree_sprites: List[pygame.Surface] = self.assets.tree_sprites
        self.grass_tiles: List[pygame.Surface] = self.assets.grass_tiles
    
    def update(self, delta_time: float):
        """Update world."""
        for entity in self.entities:
            entity.update(delta_time)
    
    def get_tile_sprite(self, tx: int, ty: int, tile_type: str) -> pygame.Surface:
        """Get sprite for tile with deterministic variation."""
        if tile_type == "grass":
            if not self.grass_tiles:
                return pygame.Surface((TILE_SIZE, TILE_SIZE))
            variant = (tx * 37 + ty * 91) % len(self.grass_tiles)
            return self.grass_tiles[variant]
        elif tile_type == "forest":
            if not self.tree_sprites:
                return pygame.Surface((TILE_SIZE, TILE_SIZE))
            variant = (tx * 73 + ty * 137) % len(self.tree_sprites)
            return self.tree_sprites[variant]
        else:
            if self.grass_tiles:
                return self.grass_tiles[0]
            return pygame.Surface((TILE_SIZE, TILE_SIZE))

# ============================================================================
# UI - HOTBAR
# ============================================================================

class Hotbar:
    """Bottom inventory bar UI."""
    
    def __init__(self, asset_manager: AssetManager):
        self.assets = asset_manager
        self.x = SCREEN_WIDTH // 2 - (INVENTORY_SLOTS * (INVENTORY_SLOT_SIZE + 5)) // 2
        self.y = SCREEN_HEIGHT - INVENTORY_SLOT_SIZE - 20
        self.selected_slot = 0
    
    def render(self, surface: pygame.Surface, inventory: List[Optional[Item]]):
        """Draw hotbar using UI assets."""
        bar_width = INVENTORY_SLOTS * (INVENTORY_SLOT_SIZE + 5) + 10

        # Background bar using ui_bg if available
        ui_bg = self.assets.ui.get("ui_bg")
        if ui_bg:
            bg_scaled = pygame.transform.scale(ui_bg, (bar_width, INVENTORY_SLOT_SIZE + 20))
            surface.blit(bg_scaled, (self.x - 5, self.y - 10))

        # Slots and items
        for i in range(INVENTORY_SLOTS):
            slot_x = self.x + i * (INVENTORY_SLOT_SIZE + 5)
            slot_y = self.y

            # Selection frame (level_frame asset)
            if i == self.selected_slot:
                frame = self.assets.ui.get("level_frame")
                if frame:
                    frame_scaled = pygame.transform.scale(frame, (INVENTORY_SLOT_SIZE, INVENTORY_SLOT_SIZE))
                    surface.blit(frame_scaled, (slot_x, slot_y))

            # Item display
            item = inventory[i]
            if item and item.image_key:
                img = self.assets.item_images.get(item.image_key)
                if img:
                    surface.blit(img, (slot_x, slot_y))

# ============================================================================
# UI - SHOP
# ============================================================================

class ShopUI:
    """Shop/merchant interface (Phillip's Shop from screenshot)."""
    
    def __init__(self, asset_manager: AssetManager):
        self.assets = asset_manager
        # Shop items arranged in grid from screenshot
        self.items = [
            Item("Pickaxe", ItemType.TOOL, 1, 1, 200, image_key="pickaxe"),
            Item("Axe", ItemType.TOOL, 1, 1, 180, image_key="axe"),
            Item("Seed Packet", ItemType.SEED, 5, 99, 15, image_key="seed_packet"),
            Item("Birch Log", ItemType.RESOURCE, 3, 99, 25, image_key="birch_log"),
            Item("Oak Log", ItemType.RESOURCE, 3, 99, 25, image_key="oak_log"),
            
            Item("Spruce Log", ItemType.RESOURCE, 3, 99, 25, image_key="spruce_log"),
            Item("Elderberry Log", ItemType.RESOURCE, 2, 99, 35, image_key="elderberry_log"),
            Item("Crop Seed", ItemType.SEED, 10, 99, 10, image_key="seed_packet"),
            Item("Pouch", ItemType.RESOURCE, 1, 1, 100, image_key="pouch"),
            Item("Crop Bundle", ItemType.CROP, 1, 99, 25, image_key="crop_sheet"),
        ]
        self.visible = False
        self.selected_item: Optional[Item] = None
        self.selected_item_index = -1
    
    def render(self, surface: pygame.Surface):
        """Draw shop UI (exact layout from Philip's Shop screenshot)."""
        if not self.visible:
            return
        
        # Shop panel - positioned like in screenshot
        panel_x = 470
        panel_y = 60
        panel_w = 450
        panel_h = 500
        
        # Panel background using ui_bg asset if available
        ui_bg = self.assets.ui.get("ui_bg")
        if ui_bg:
            panel_bg = pygame.transform.scale(ui_bg, (panel_w, panel_h))
            surface.blit(panel_bg, (panel_x, panel_y))
        else:
            pygame.draw.rect(surface, (100, 180, 100),
                            (panel_x, panel_y, panel_w, panel_h))
            pygame.draw.rect(surface, COLOR_WOOD_BORDER,
                            (panel_x, panel_y, panel_w, panel_h), 5)
        
        # Title bar using ui_bar asset
        ui_bar = self.assets.ui.get("ui_bar")
        if ui_bar:
            bar = pygame.transform.scale(ui_bar, (panel_w, 40))
            surface.blit(bar, (panel_x, panel_y))
        else:
            pygame.draw.rect(surface, COLOR_ACCENT_ORANGE,
                            (panel_x, panel_y, panel_w, 40))
        font_title = pygame.font.Font(None, 28)
        title = font_title.render("Phillip's Shop", True, COLOR_TEXT_LIGHT)
        surface.blit(title, (panel_x + 20, panel_y + 8))
        
        # Item grid (5 columns x 5 rows) - dark background
        grid_x = panel_x + 15
        grid_y = panel_y + 55
        grid_cols = 5
        grid_rows = 5
        item_size = SHOP_ITEM_SIZE
        spacing = 8
        
        # Grid background (dark)
        grid_bg_w = grid_cols * item_size + (grid_cols - 1) * spacing
        grid_bg_h = grid_rows * item_size + (grid_rows - 1) * spacing
        pygame.draw.rect(surface, COLOR_DARK_BG,
                (grid_x - 5, grid_y - 5, grid_bg_w + 10, grid_bg_h + 10))
        
        # Draw items in grid
        for idx, item in enumerate(self.items[:grid_cols * grid_rows]):
            col = idx % grid_cols
            row = idx // grid_cols
            
            item_x = grid_x + col * (item_size + spacing)
            item_y = grid_y + row * (item_size + spacing)
            
            # Item slot background
            pygame.draw.rect(surface, (50, 50, 50),
                            (item_x, item_y, item_size, item_size))
            
            # Item image
            if item.image_key and item.image_key in self.assets.item_images:
                img = self.assets.item_images[item.image_key]
                img_scaled = pygame.transform.scale(img, (item_size - 8, item_size - 8))
                surface.blit(img_scaled, (item_x + 4, item_y + 4))

            # Selection frame
            if idx == self.selected_item_index:
                frame = self.assets.ui.get("level_frame")
                if frame:
                    frame_scaled = pygame.transform.scale(frame, (item_size, item_size))
                    surface.blit(frame_scaled, (item_x, item_y))
        
        # Info panel (bottom left)
        info_x = panel_x + 15
        info_y = panel_y + 320
        info_w = 200
        info_h = 160
        
        info_bg = self.assets.ui.get("ui_bg")
        if info_bg:
            info_scaled = pygame.transform.scale(info_bg, (info_w, info_h))
            surface.blit(info_scaled, (info_x, info_y))
        else:
            pygame.draw.rect(surface, COLOR_WOOD_LIGHT,
                            (info_x, info_y, info_w, info_h))
            pygame.draw.rect(surface, COLOR_WOOD_BORDER,
                            (info_x, info_y, info_w, info_h), 2)
        
        if self.selected_item_index >= 0 and self.selected_item_index < len(self.items):
            item = self.items[self.selected_item_index]
            font_small = pygame.font.Font(None, 16)
            font_med = pygame.font.Font(None, 18)
            
            # Item name
            name_surf = font_med.render(f"Name: {item.name}", True, COLOR_TEXT_DARK)
            surface.blit(name_surf, (info_x + 10, info_y + 10))
            
            # Use
            use_text = {
                ItemType.TOOL: "Tool/Work",
                ItemType.SEED: "Plant/Farm",
                ItemType.CROP: "Food/Crafting",
                ItemType.RESOURCE: "Building",
                ItemType.BUILDING: "Place/Build",
            }
            use_surf = font_small.render(f"Use: {use_text.get(item.item_type, 'Unknown')}", 
                                        True, COLOR_TEXT_DARK)
            surface.blit(use_surf, (info_x + 10, info_y + 35))
            
            # Rarity
            rarity_surf = font_small.render(f"Rarity: Common", True, COLOR_TEXT_DARK)
            surface.blit(rarity_surf, (info_x + 10, info_y + 55))
        
        # Quantity display (1/5)
        qty_x = panel_x + 20
        qty_y = panel_y + 485
        qty_surf = pygame.font.Font(None, 24).render("1/5", True, COLOR_TEXT_LIGHT)
        qty_bg = self.assets.ui.get("ui_bar")
        if qty_bg:
            qty_scaled = pygame.transform.scale(qty_bg, (80, 30))
            surface.blit(qty_scaled, (qty_x - 5, qty_y - 5))
        surface.blit(qty_surf, (qty_x, qty_y))
        
        # BUY button (left - green)
        buy_x = qty_x + 80
        buy_y = qty_y
        buy_w = 60
        buy_h = 30
        buy_bg = self.assets.ui.get("ui_bar")
        if buy_bg:
            buy_scaled = pygame.transform.scale(buy_bg, (buy_w, buy_h))
            surface.blit(buy_scaled, (buy_x, buy_y))
        else:
            pygame.draw.rect(surface, (100, 200, 100), (buy_x, buy_y, buy_w, buy_h))
        buy_text = pygame.font.Font(None, 18).render("BUY", True, COLOR_TEXT_LIGHT)
        buy_text_rect = buy_text.get_rect(center=(buy_x + buy_w // 2, buy_y + buy_h // 2))
        surface.blit(buy_text, buy_text_rect)
        
        # DISMISS button (right - blue)
        dismiss_x = buy_x + 80
        dismiss_y = buy_y
        dismiss_w = 80
        dismiss_h = 30
        dismiss_bg = self.assets.ui.get("ui_bar")
        if dismiss_bg:
            dismiss_scaled = pygame.transform.scale(dismiss_bg, (dismiss_w, dismiss_h))
            surface.blit(dismiss_scaled, (dismiss_x, dismiss_y))
        else:
            pygame.draw.rect(surface, (100, 150, 200), (dismiss_x, dismiss_y, dismiss_w, dismiss_h))
        dismiss_text = pygame.font.Font(None, 18).render("DISMISS", True, COLOR_TEXT_LIGHT)
        dismiss_text_rect = dismiss_text.get_rect(center=(dismiss_x + dismiss_w // 2, dismiss_y + dismiss_h // 2))
        surface.blit(dismiss_text, dismiss_text_rect)

# ============================================================================
# MAIN GAME ENGINE
# ============================================================================

class CroptopiaEngine:
    """Main game engine."""
    
    def __init__(self):
        """Initialize engine."""
        pygame.init()
        
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Croptopia - Native Engine")
        
        self.clock = pygame.time.Clock()
        self.running = True
        self.game_state = GameState.WORLD
        
        # Game systems
        self.world = GameWorld()
        self.scene = World2Scene(self.world.assets)
        self.hotbar = Hotbar(self.world.assets)
        self.shop = ShopUI(self.world.assets)
        
        # Camera (follows player)
        self.camera_x = 0.0
        self.camera_y = 0.0
        
        # Time system
        self.game_time = 0.0
        self.day = 1
        self.hour = 8
        self.minute = 0
    
    def handle_events(self):
        """Handle input."""
        keys = pygame.key.get_pressed()
        
        # Movement (only when shop not open)
        if not self.shop.visible:
            self.world.player.velocity_x = 0
            self.world.player.velocity_y = 0
            
            if keys[pygame.K_UP] or keys[pygame.K_w]:
                self.world.player.velocity_y = -self.world.player.speed
                self.world.player.facing_direction = Direction.UP
            if keys[pygame.K_DOWN] or keys[pygame.K_s]:
                self.world.player.velocity_y = self.world.player.speed
                self.world.player.facing_direction = Direction.DOWN
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                self.world.player.velocity_x = -self.world.player.speed
                self.world.player.facing_direction = Direction.LEFT
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                self.world.player.velocity_x = self.world.player.speed
                self.world.player.facing_direction = Direction.RIGHT
        
        # Events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.shop.visible = False
                
                elif event.key == pygame.K_TAB:
                    # Toggle shop
                    self.shop.visible = not self.shop.visible
                
                # Hotbar slots
                elif event.key == pygame.K_1:
                    self.hotbar.selected_slot = 0
                elif event.key == pygame.K_2:
                    self.hotbar.selected_slot = 1
                elif event.key == pygame.K_3:
                    self.hotbar.selected_slot = 2
                elif event.key == pygame.K_4:
                    self.hotbar.selected_slot = 3
                elif event.key == pygame.K_5:
                    self.hotbar.selected_slot = 4
                elif event.key == pygame.K_6:
                    self.hotbar.selected_slot = 5
                elif event.key == pygame.K_7:
                    self.hotbar.selected_slot = 6
                elif event.key == pygame.K_8:
                    self.hotbar.selected_slot = 7
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if self.shop.visible:
                    self._handle_shop_click(event.pos)
    
    def _handle_shop_click(self, pos: Tuple[int, int]):
        """Handle clicks in shop UI."""
        x, y = pos
        
        # Grid item selection
        grid_x = 485
        grid_y = 115
        item_size = SHOP_ITEM_SIZE
        spacing = 8
        grid_cols = 5
        
        for idx in range(grid_cols * 5):
            col = idx % grid_cols
            row = idx // grid_cols
            
            item_x = grid_x + col * (item_size + spacing)
            item_y = grid_y + row * (item_size + spacing)
            
            if (item_x <= x <= item_x + item_size and 
                item_y <= y <= item_y + item_size):
                self.shop.selected_item_index = idx
                break
    
    def update(self, delta_time: float):
        """Update game logic."""
        self.world.update(delta_time)
        
        # Update time
        self.game_time += delta_time * GAME_TIME_SCALE
        self.minute = int(self.game_time) % 60
        self.hour = 8 + (int(self.game_time) // 60) % 24
        
        # Update camera to follow player
        self.camera_x = self.world.player.x - SCREEN_WIDTH // 2 + TILE_SIZE // 2
        self.camera_y = self.world.player.y - SCREEN_HEIGHT // 2 + TILE_SIZE // 2
    
    def render(self):
        """Render game."""
        self.screen.fill(COLOR_GRASS)
        
        # Draw base grass layer
        tile_start_x = max(0, int(self.camera_x // TILE_SIZE))
        tile_start_y = max(0, int(self.camera_y // TILE_SIZE))
        tile_end_x = min(self.world.tilemap.width, 
                         tile_start_x + (SCREEN_WIDTH // TILE_SIZE) + 2)
        tile_end_y = min(self.world.tilemap.height,
                         tile_start_y + (SCREEN_HEIGHT // TILE_SIZE) + 2)
        
        for ty in range(tile_start_y, tile_end_y):
            for tx in range(tile_start_x, tile_end_x):
                tile_type = self.world.tilemap.get_tile(tx, ty)
                sprite = self.world.get_tile_sprite(tx, ty, tile_type)
                
                screen_x = tx * TILE_SIZE - self.camera_x
                screen_y = ty * TILE_SIZE - self.camera_y

                self.screen.blit(sprite, (screen_x, screen_y))

        # Draw World 2 layers from Godot scene
        self.scene.render(self.screen, self.camera_x, self.camera_y)
        
        # Draw entities
        for entity in self.world.entities:
            screen_x = entity.x - self.camera_x
            screen_y = entity.y - self.camera_y
            self.screen.blit(entity.sprite.image, (screen_x, screen_y))
        
        # Draw UI
        self.hotbar.render(self.screen, self.world.player.inventory)
        self.shop.render(self.screen)
        
        # Draw HUD
        self._draw_hud()
        
        pygame.display.flip()
    
    def _draw_hud(self):
        """Draw heads-up display."""
        font_small = pygame.font.Font(None, 18)
        font_large = pygame.font.Font(None, 28)
        
        # Time display (top left)
        time_text = f"Day {self.day}, {self.hour:02d}:{self.minute:02d}"
        time_surface = font_large.render(time_text, True, COLOR_TEXT_LIGHT)
        
        # Add background for readability
        bg_rect = time_surface.get_rect()
        bg_rect.topleft = (10, 10)
        ui_bar = self.world.assets.ui.get("ui_bar")
        if ui_bar:
            bar = pygame.transform.scale(ui_bar, (bg_rect.width + 20, bg_rect.height + 10))
            self.screen.blit(bar, (5, 5))
        else:
            pygame.draw.rect(self.screen, (0, 0, 0), bg_rect.inflate(10, 10))
        self.screen.blit(time_surface, (15, 15))
        
        # Zone display (top right)
        zone_text = "Zone: World 2"
        zone_surface = font_large.render(zone_text, True, COLOR_TEXT_LIGHT)
        zone_rect = zone_surface.get_rect()
        zone_rect.topright = (SCREEN_WIDTH - 10, 10)
        
        bg_rect = zone_rect.copy()
        if ui_bar:
            bar = pygame.transform.scale(ui_bar, (bg_rect.width + 20, bg_rect.height + 10))
            self.screen.blit(bar, (zone_rect.x - 10, zone_rect.y - 5))
        else:
            pygame.draw.rect(self.screen, (0, 0, 0), bg_rect.inflate(10, 10))
        self.screen.blit(zone_surface, (zone_rect.x - 5, zone_rect.y + 5))
        
        # FPS
        fps = int(self.clock.get_fps())
        fps_text = font_small.render(f"FPS: {fps}", True, COLOR_TEXT_LIGHT)
        self.screen.blit(fps_text, (10, SCREEN_HEIGHT - 30))
    
    def run(self):
        """Main game loop."""
        while self.running:
            delta_time = self.clock.tick(FRAME_RATE) / 1000.0  # Convert to seconds
            
            self.handle_events()
            self.update(delta_time)
            self.render()
        
        pygame.quit()
        sys.exit()

# ============================================================================
# ENTRY POINT
# ============================================================================

def main():
    """Start the game."""
    engine = CroptopiaEngine()
    engine.run()

if __name__ == "__main__":
    main()
