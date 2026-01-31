"""
TileMap Loader - Parses Godot spawn_node.tscn and extracts tilemap data
"""

import re
from typing import Dict, List, Tuple, Any
from pathlib import Path


class TileMapLoader:
    """Loads and parses Godot TileMap data from .tscn files"""
    
    def __init__(self, tscn_path: str):
        """Initialize loader with path to spawn_node.tscn"""
        self.tscn_path = Path(tscn_path)
        self.tileset_data = {}
        self.layer_data = {}
        self.tile_size = 32  # Default Croptopia tile size
        
    def load(self) -> Dict[str, Any]:
        """Load and parse the tilemap data"""
        if not self.tscn_path.exists():
            print(f"[TileMapLoader] ERROR: {self.tscn_path} not found")
            return {}
        
        print(f"[TileMapLoader] Loading from {self.tscn_path}")
        
        with open(self.tscn_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract texture paths
        self._parse_textures(content)
        
        # Extract layer data
        self._parse_layers(content)
        
        print(f"[TileMapLoader] Loaded {len(self.tileset_data)} textures")
        print(f"[TileMapLoader] Loaded {len(self.layer_data)} layers")
        
        return {
            'textures': self.tileset_data,
            'layers': self.layer_data,
            'tile_size': self.tile_size
        }
    
    def _parse_textures(self, content: str) -> None:
        """Extract texture file paths from ExtResource declarations"""
        # Pattern: [ext_resource type="Texture2D" uid="..." path="res://assets/filename.png" id="..."]
        pattern = r'\[ext_resource type="Texture2D".*?path="(res://assets/[^"]+)".*?id="([^"]+)"\]'
        
        matches = re.finditer(pattern, content)
        for match in matches:
            resource_path = match.group(1)
            resource_id = match.group(2)
            
            # Convert res://assets/filename.png to actual file path
            filename = resource_path.split('/')[-1]
            self.tileset_data[resource_id] = filename
    
    def _parse_layers(self, content: str) -> None:
        """Extract layer definitions and tile data"""
        # Look for layer definitions
        layer_pattern = r'layer_(\d+)/name = "([^"]+)".*?layer_\d+/tile_data = PackedInt32Array\(([^)]*)\)'
        
        matches = re.finditer(layer_pattern, content, re.DOTALL)
        for match in matches:
            layer_idx = match.group(1)
            layer_name = match.group(2)
            tile_data_str = match.group(3)
            
            # Parse tile data (complex format from Godot)
            tiles = self._parse_tile_data(tile_data_str)
            
            self.layer_data[int(layer_idx)] = {
                'name': layer_name,
                'tiles': tiles
            }
    
    def _parse_tile_data(self, data_str: str) -> List[Tuple[int, int, int]]:
        """
        Parse Godot's PackedInt32Array tile data format.
        Format: [x, source_id, tile_id, x, source_id, tile_id, ...]
        Each tile is defined by 3 integers.
        """
        if not data_str.strip():
            return []
        
        # Split and convert to integers
        try:
            numbers = [int(n.strip()) for n in data_str.split(',') if n.strip()]
        except ValueError:
            return []
        
        # Group into tiles (every 3 integers)
        tiles = []
        for i in range(0, len(numbers) - 2, 3):
            tile_pos = numbers[i]  # Encoded position
            source_id = numbers[i + 1]
            tile_id = numbers[i + 2]
            
            # Decode position from Godot's int64 encoding
            x = (tile_pos & 0xFFFFFFFF) >> 0
            y = (tile_pos >> 32) & 0xFFFFFFFF
            
            # Handle negative coordinates
            if x > 0x80000000:
                x = x - 0x100000000
            if y > 0x80000000:
                y = y - 0x100000000
            
            tiles.append((x, y, source_id, tile_id))
        
        return tiles
    
    def get_texture_path(self, asset_folder: str, resource_id: str) -> str:
        """Convert resource ID to actual file path"""
        if resource_id not in self.tileset_data:
            return None
        
        filename = self.tileset_data[resource_id]
        return f"{asset_folder}/{filename}"
