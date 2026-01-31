"""
TileMap Renderer - Multi-layer rendering with asset mapping
Replaces tilemap.gd and terrain.gd (400+ lines combined)
"""

import pygame
from croptopia.signals import SignalEmitter
from typing import Dict, List, Tuple, Set
import struct


class TileMapRenderer(SignalEmitter):
    """
    Renders 6-layer tilemap from Godot project using texture assets.
    Replaces tilemap.gd (200 lines) and terrain.gd (200 lines).
    
    Key Features:
    - 6-layer rendering system (grass, decoration, shadow, collision, highlight, effect)
    - PackedInt32Array decoding (Godot's binary tile format)
    - 220+ texture asset mapping
    - Viewport culling for performance
    - Layer visibility toggling
    - Collision data extraction
    """
    
    # Layer definitions matching tilemap.gd and terrain.gd
    LAYERS = {
        'grass': 0,           # Base grass layer
        'decoration': 1,      # Objects, trees, bushes
        'shadow': 2,          # Shadow effects
        'collision': 3,       # Collision data (not rendered)
        'highlight': 4,       # Interaction highlight
        'effect': 5           # Effects, particles
    }
    
    # Tile size constants
    TILE_WIDTH = 16
    TILE_HEIGHT = 16
    
    # Viewport culling
    CULL_MARGIN = 32  # Extra tiles around viewport to avoid popping
    
    def __init__(self, tilemap_data: Dict = None, assets: Dict = None):
        """
        Initialize tilemap renderer.
        
        Args:
            tilemap_data: Parsed tilemap data from .tscn files
            assets: Dictionary of loaded texture assets
        """
        super().__init__()
        
        # Tilemap data structure:
        # {
        #   'layer_name': {
        #     (x, y): tile_id
        #   }
        # }
        self.tilemap_data = tilemap_data or {}
        self.assets = assets or {}
        
        # Layer visibility
        self.layer_visibility = {
            'grass': True,
            'decoration': True,
            'shadow': True,
            'collision': False,  # Don't render collision by default
            'highlight': False,  # Only show when needed
            'effect': True
        }
        
        # Cache for culled tiles
        self.visible_tiles: Dict[str, Set[Tuple[int, int]]] = {}
        self.last_camera_pos = None
        
        # Collision tiles
        self.collision_tiles: Set[Tuple[int, int]] = set()
        self._parse_collision_layer()
        
        print(f"[TileMapRenderer] Initialized with {len(self.tilemap_data)} layers")
    
    def update(self, camera_pos: pygame.math.Vector2, viewport_size: Tuple[int, int]) -> None:
        """
        Update visible tiles based on camera position.
        Implements viewport culling for performance.
        
        Args:
            camera_pos: Camera position (x, y)
            viewport_size: (width, height) of viewport in pixels
        """
        
        # Only recalculate if camera moved significantly
        if self.last_camera_pos and \
           abs(camera_pos.x - self.last_camera_pos.x) < self.TILE_WIDTH and \
           abs(camera_pos.y - self.last_camera_pos.y) < self.TILE_HEIGHT:
            return
        
        # Calculate visible tile range
        view_left = int(camera_pos.x / self.TILE_WIDTH) - self.CULL_MARGIN
        view_top = int(camera_pos.y / self.TILE_HEIGHT) - self.CULL_MARGIN
        view_right = int((camera_pos.x + viewport_size[0]) / self.TILE_WIDTH) + self.CULL_MARGIN
        view_bottom = int((camera_pos.y + viewport_size[1]) / self.TILE_HEIGHT) + self.CULL_MARGIN
        
        # Update visible tiles for each layer
        self.visible_tiles = {}
        for layer_name in self.tilemap_data:
            visible = set()
            for (x, y) in self.tilemap_data[layer_name]:
                if view_left <= x <= view_right and view_top <= y <= view_bottom:
                    visible.add((x, y))
            self.visible_tiles[layer_name] = visible
        
        self.last_camera_pos = camera_pos.copy()
    
    def render(self, display: pygame.Surface, camera_pos: pygame.math.Vector2) -> None:
        """
        Draw all visible tiles layer by layer.
        
        Args:
            display: Pygame surface to draw to
            camera_pos: Camera position for viewport conversion
        """
        
        # Render layers in order
        for layer_name in ['grass', 'decoration', 'shadow', 'highlight', 'effect']:
            if not self.layer_visibility[layer_name]:
                continue
            
            if layer_name not in self.visible_tiles:
                continue
            
            # Draw each visible tile in this layer
            for (tile_x, tile_y) in self.visible_tiles[layer_name]:
                tile_id = self.tilemap_data[layer_name][(tile_x, tile_y)]
                
                if tile_id == 0:  # Skip empty tiles
                    continue
                
                # Convert world position to screen position
                screen_x = tile_x * self.TILE_WIDTH - camera_pos.x
                screen_y = tile_y * self.TILE_HEIGHT - camera_pos.y
                
                # Draw tile
                self._draw_tile(display, tile_id, screen_x, screen_y, layer_name)
    
    def render_collision_overlay(self, display: pygame.Surface, 
                                camera_pos: pygame.math.Vector2, 
                                opacity: int = 100) -> None:
        """
        Render collision layer as semi-transparent overlay.
        Useful for debugging.
        
        Args:
            display: Pygame surface to draw to
            camera_pos: Camera position
            opacity: Transparency (0-255)
        """
        
        # Create collision surface
        collision_surf = pygame.Surface((display.get_width(), display.get_height()))
        collision_surf.set_alpha(opacity)
        collision_surf.fill((0, 0, 0))  # Transparent black
        
        # Draw collision tiles
        for (tile_x, tile_y) in self.collision_tiles:
            screen_x = tile_x * self.TILE_WIDTH - camera_pos.x
            screen_y = tile_y * self.TILE_HEIGHT - camera_pos.y
            
            if -16 < screen_x < display.get_width() and \
               -16 < screen_y < display.get_height():
                pygame.draw.rect(collision_surf, (255, 0, 0), 
                               (screen_x, screen_y, self.TILE_WIDTH, self.TILE_HEIGHT), 1)
        
        display.blit(collision_surf, (0, 0))
    
    def get_collision_tiles(self) -> Set[Tuple[int, int]]:
        """
        Get set of all collision tiles.
        Used for movement validation.
        
        Returns:
            Set of (x, y) tile coordinates with collision
        """
        return self.collision_tiles.copy()
    
    def is_walkable(self, world_x: float, world_y: float) -> bool:
        """
        Check if position is walkable (no collision).
        
        Args:
            world_x: World position X
            world_y: World position Y
        
        Returns:
            True if position is walkable
        """
        
        tile_x = int(world_x / self.TILE_WIDTH)
        tile_y = int(world_y / self.TILE_HEIGHT)
        
        return (tile_x, tile_y) not in self.collision_tiles
    
    def set_layer_visibility(self, layer_name: str, visible: bool) -> None:
        """
        Toggle layer visibility.
        
        Args:
            layer_name: Name of layer
            visible: Whether to show layer
        """
        
        if layer_name in self.layer_visibility:
            self.layer_visibility[layer_name] = visible
            print(f"[TileMapRenderer] Layer '{layer_name}' visibility: {visible}")
    
    def _draw_tile(self, display: pygame.Surface, tile_id: int, 
                  screen_x: float, screen_y: float, layer_name: str) -> None:
        """
        Draw a single tile sprite.
        
        Args:
            display: Pygame surface to draw to
            tile_id: Tile ID from tilemap data
            screen_x: Screen X coordinate
            screen_y: Screen Y coordinate
            layer_name: Name of layer (for asset lookup)
        """
        
        # Get asset key for this tile
        asset_key = f"tile_{layer_name}_{tile_id}"
        
        if asset_key in self.assets:
            sprite = self.assets[asset_key]
            display.blit(sprite, (int(screen_x), int(screen_y)))
        else:
            # Draw placeholder rect if asset not found
            color = self._get_layer_color(layer_name)
            pygame.draw.rect(display, color, 
                           (int(screen_x), int(screen_y), 
                            self.TILE_WIDTH, self.TILE_HEIGHT), 1)
    
    def _get_layer_color(self, layer_name: str) -> Tuple[int, int, int]:
        """Get placeholder color for layer"""
        colors = {
            'grass': (34, 139, 34),
            'decoration': (139, 69, 19),
            'shadow': (50, 50, 50),
            'collision': (255, 0, 0),
            'highlight': (255, 255, 0),
            'effect': (255, 0, 255)
        }
        return colors.get(layer_name, (200, 200, 200))
    
    def _parse_collision_layer(self) -> None:
        """
        Extract collision data from collision layer.
        Populates self.collision_tiles set.
        """
        
        if 'collision' not in self.tilemap_data:
            return
        
        for (tile_x, tile_y), tile_id in self.tilemap_data['collision'].items():
            if tile_id != 0:  # Non-zero = collision
                self.collision_tiles.add((tile_x, tile_y))
        
        print(f"[TileMapRenderer] Found {len(self.collision_tiles)} collision tiles")
    
    @staticmethod
    def decode_packed_int32_array(packed_data: bytes) -> List[int]:
        """
        Decode Godot PackedInt32Array from binary.
        Godot stores as little-endian 32-bit integers.
        
        Args:
            packed_data: Binary data from Godot
        
        Returns:
            List of integers
        """
        
        result = []
        for i in range(0, len(packed_data), 4):
            if i + 4 <= len(packed_data):
                value = struct.unpack('<I', packed_data[i:i+4])[0]
                result.append(value)
        
        return result
    
    @staticmethod
    def decode_tile_position(packed_value: int) -> Tuple[int, int]:
        """
        Decode tile position from PackedInt32Array value.
        Godot stores: x in lower 16 bits, y in upper 16 bits
        
        Args:
            packed_value: Packed 32-bit integer
        
        Returns:
            (x, y) tile coordinates
        """
        
        x = packed_value & 0xFFFF
        y = (packed_value >> 16) & 0xFFFF
        
        # Handle negative coordinates (Godot uses signed)
        if x > 32767:
            x -= 65536
        if y > 32767:
            y -= 65536
        
        return (x, y)
    
    @staticmethod
    def load_tilemap_from_tscn(filepath: str) -> Dict:
        """
        Load tilemap data from Godot .tscn file.
        Parses tile_data resources.
        
        Args:
            filepath: Path to .tscn file
        
        Returns:
            Dictionary with layer data
        """
        
        # TODO: Implement .tscn parser
        # This would read the file and extract TileMapLayer resources
        # For now, return empty structure
        
        tilemap_data = {
            'grass': {},
            'decoration': {},
            'shadow': {},
            'collision': {},
            'highlight': {},
            'effect': {}
        }
        
        print(f"[TileMapRenderer] Loading tilemap from {filepath}")
        
        return tilemap_data


# Testing
if __name__ == "__main__":
    pygame.init()
    display = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("TileMap Renderer Test")
    
    # Create test tilemap data
    test_data = {
        'grass': {
            (0, 0): 1, (1, 0): 1, (0, 1): 1, (1, 1): 1,
        },
        'decoration': {
            (1, 0): 5,  # Tree
        },
        'collision': {
            (1, 0): 1,  # Tree collision
        }
    }
    
    renderer = TileMapRenderer(test_data)
    
    print("\nTileMapRenderer Test")
    print("=" * 50)
    print(f"Tilemap layers: {list(renderer.tilemap_data.keys())}")
    print(f"Collision tiles: {renderer.collision_tiles}")
    
    # Test walkability
    print("\nWalkability test:")
    print(f"Position (0, 0) walkable: {renderer.is_walkable(0, 0)}")
    print(f"Position (16, 0) walkable: {renderer.is_walkable(16, 0)}")
    
    # Test position decoding
    print("\nPosition decoding test:")
    packed = (100 & 0xFFFF) | ((50 & 0xFFFF) << 16)
    x, y = renderer.decode_tile_position(packed)
    print(f"Packed value {packed} decodes to ({x}, {y})")
    
    pygame.quit()
