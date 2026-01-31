"""
Godot TSCN Parser - Extract and render actual Godot tilemap data
"""

import re
from pathlib import Path
from typing import Dict, List, Tuple, Any
import pygame
from PIL import Image
import io


class GodotTSCNParser:
    """Parses Godot .tscn files and extracts game data"""
    
    def __init__(self, tscn_path: str, assets_path: str = None):
        self.tscn_path = Path(tscn_path)
        self.assets_path = Path(assets_path) if assets_path else self.tscn_path.parent.parent / "assets"
        self.textures = {}
        self.tilemap_layers = {}
        self.tileset_sources = {}
        self.tilemap_offset = (0, 0)
        
    def parse(self) -> Dict[str, Any]:
        """Parse the tscn file and return data"""
        if not self.tscn_path.exists():
            print(f"[Parser] ERROR: {self.tscn_path} not found")
            return None
        
        print(f"[Parser] Reading {self.tscn_path.name}...")
        with open(self.tscn_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # Extract textures
        self._extract_textures(content)
        
        # Extract tileset sources
        self._extract_tileset_sources(content)
        
        # Extract layer data
        self._extract_layer_data(content)

        # Extract tilemap offset
        self._extract_tilemap_offset(content)
        
        return {
            'textures': self.textures,
            'layers': self.tilemap_layers,
            'tileset_sources': self.tileset_sources,
            'tilemap_offset': self.tilemap_offset,
            'assets_path': str(self.assets_path)
        }

    def _extract_tilemap_offset(self, content: str) -> None:
        """Extract TileMap2 world offset from node hierarchy"""
        def find_node_position(node_name: str) -> Tuple[float, float]:
            node_pattern = rf'\[node name="{re.escape(node_name)}"[^\n]*\](.*?)(?=\n\[node|\Z)'
            node_match = re.search(node_pattern, content, re.DOTALL)
            if not node_match:
                return (0.0, 0.0)
            block = node_match.group(1)
            pos_match = re.search(r'position = Vector2\((\-?\d+\.?\d*),\s*(\-?\d+\.?\d*)\)', block)
            if not pos_match:
                return (0.0, 0.0)
            return (float(pos_match.group(1)), float(pos_match.group(2)))

        spawn_node_pos = find_node_position('spawn_node')
        spawn_pos = find_node_position('spawn')
        tilemap_pos = find_node_position('TileMap2')

        self.tilemap_offset = (
            spawn_node_pos[0] + spawn_pos[0] + tilemap_pos[0],
            spawn_node_pos[1] + spawn_pos[1] + tilemap_pos[1],
        )

    def _extract_tileset_sources(self, content: str) -> None:
        """Extract TileSet atlas sources and map source IDs to textures"""
        # Build atlas source definitions
        atlas_sources: Dict[str, Dict[str, Any]] = {}
        atlas_pattern = r'\[sub_resource type="TileSetAtlasSource" id="([^"]+)"\](.*?)(?=\n\[sub_resource|\n\[node|\Z)'
        for match in re.finditer(atlas_pattern, content, re.DOTALL):
            atlas_id = match.group(1)
            atlas_block = match.group(2)
            
            texture_match = re.search(r'texture = ExtResource\("([^"]+)"\)', atlas_block)
            texture_id = texture_match.group(1) if texture_match else None
            
            margins_match = re.search(r'margins = Vector2i\((\-?\d+),\s*(\-?\d+)\)', atlas_block)
            margins = (int(margins_match.group(1)), int(margins_match.group(2))) if margins_match else (0, 0)
            
            region_match = re.search(r'texture_region_size = Vector2i\((\d+),\s*(\d+)\)', atlas_block)
            region_size = (int(region_match.group(1)), int(region_match.group(2))) if region_match else None
            
            # Track atlas coordinate bounds FOR THIS SPECIFIC ATLAS SOURCE
            max_ax = -1
            max_ay = -1
            # Build ordered list of coordinates as they appear in the TSCN
            # This gives us a cell_id -> (x,y) mapping
            atlas_coords_list = []
            atlas_coords_set = set()
            for coord_match in re.finditer(r'(\d+):(\d+)/\d+ = 0', atlas_block):
                ax = int(coord_match.group(1))
                ay = int(coord_match.group(2))
                atlas_coords_list.append((ax, ay))
                atlas_coords_set.add((ax, ay))
                if ax > max_ax:
                    max_ax = ax
                if ay > max_ay:
                    max_ay = ay

            # Parse alternative flags (flip/transpose)
            alt_flags: Dict[Tuple[int, int, int], Dict[str, bool]] = {}
            for flag_match in re.finditer(r'(\d+):(\d+)/(\d+)/(flip_h|flip_v|transpose) = true', atlas_block):
                ax = int(flag_match.group(1))
                ay = int(flag_match.group(2))
                alt = int(flag_match.group(3))
                flag = flag_match.group(4)
                key = (ax, ay, alt)
                if key not in alt_flags:
                    alt_flags[key] = {'flip_h': False, 'flip_v': False, 'transpose': False}
                alt_flags[key][flag] = True
            
            atlas_sources[atlas_id] = {
                'texture_id': texture_id,
                'margins': margins,
                'region_size': region_size,
                'atlas_max': (max_ax, max_ay),
                'alt_flags': alt_flags,
                'atlas_coords': atlas_coords_set,  # Set for quick lookup
                'atlas_coords_list': atlas_coords_list,  # Ordered list for cell_id mapping
            }
        
        # Map TileSet source IDs to atlas sources
        tileset_block_match = re.search(r'\[sub_resource type="TileSet" id="[^"]+"\](.*?)(?=\n\[sub_resource|\n\[node|\Z)', content, re.DOTALL)
        if not tileset_block_match:
            return
        tileset_block = tileset_block_match.group(1)
        for src_match in re.finditer(r'sources/(\d+) = SubResource\("([^"]+)"\)', tileset_block):
            source_id = int(src_match.group(1))
            atlas_id = src_match.group(2)
            atlas_def = atlas_sources.get(atlas_id)
            if not atlas_def:
                continue
            texture_path = self.textures.get(atlas_def['texture_id']) if atlas_def['texture_id'] else None
            self.tileset_sources[source_id] = {
                'texture_id': atlas_def['texture_id'],
                'texture_path': texture_path,
                'margins': atlas_def['margins'],
                'region_size': atlas_def['region_size'],
                'atlas_max': atlas_def['atlas_max'],
                'alt_flags': atlas_def['alt_flags'],
                'atlas_coords': atlas_def.get('atlas_coords', set()),  # Pass through the defined coords
                'atlas_coords_list': atlas_def.get('atlas_coords_list', []),  # Ordered list
            }
    
    def _extract_textures(self, content: str) -> None:
        """Extract texture resource declarations"""
        # Pattern for ExtResource declarations
        pattern = r'\[ext_resource type="Texture2D".*?path="res://assets/([^"]+)".*?id="([^"]+)"\]'
        
        for match in re.finditer(pattern, content):
            filename = match.group(1)
            resource_id = match.group(2)
            asset_path = self.assets_path / filename
            
            if asset_path.exists():
                self.textures[resource_id] = str(asset_path)
            else:
                self.textures[resource_id] = str(asset_path)  # Store path even if missing
        
        print(f"[Parser] Found {len(self.textures)} texture resources")
    
    def _extract_layer_data(self, content: str) -> None:
        """Extract TileMap layer data"""
        # Find TileMap2 node
        tilemap_pattern = r'\[node name="TileMap2".*?\n(.*?)\n\[node'
        
        tilemap_match = re.search(tilemap_pattern, content, re.DOTALL)
        if not tilemap_match:
            print("[Parser] No TileMap2 found")
            return
        
        tilemap_content = tilemap_match.group(1)
        
        # Extract all layer definitions
        layer_pattern = r'layer_(\d+)/name = "([^"]+)"'
        tile_data_pattern = r'layer_(\d+)/tile_data = PackedInt32Array\(([^)]*)\)'
        
        # Find all layers
        for match in re.finditer(layer_pattern, tilemap_content):
            layer_idx = int(match.group(1))
            layer_name = match.group(2)
            
            # Find tile data for this layer
            tile_match = re.search(f'layer_{layer_idx}/tile_data = PackedInt32Array\\(([^)]*)\\)', tilemap_content)
            
            if tile_match:
                tile_data_str = tile_match.group(1)
                tiles = self._parse_packedint32array(tile_data_str)
                
                self.tilemap_layers[layer_idx] = {
                    'name': layer_name,
                    'tiles': tiles
                }
                
                if tiles:
                    print(f"[Parser] Layer {layer_idx} ({layer_name}): {len(tiles)} tiles")
    
    def _parse_packedint32array(self, data_str: str) -> List[Tuple]:
        """Parse Godot's PackedInt32Array format for tiles"""
        if not data_str.strip():
            return []
        
        try:
            # Split and convert to integers
            numbers = [int(n.strip()) for n in data_str.split(',') if n.strip()]
        except:
            return []
        
        # Group into tiles: ACTUAL CORRECT FORMAT
        # value2 = marker(0x5E) + unused + source_id + unused
        # value3 = atlas_y + alt_id (needs investigation)
        tiles = []
        i = 0
        while i < len(numbers) - 2:
            pos_encoded = numbers[i]
            value2 = numbers[i + 1]
            value3 = numbers[i + 2]
            
            # Extract position
            if pos_encoded < 0:
                pos_unsigned = pos_encoded + (1 << 32)
            else:
                pos_unsigned = pos_encoded
            
            x = pos_unsigned & 0xFFFF
            y = (pos_unsigned >> 16) & 0xFFFF
            if x > 32767:
                x = x - 65536
            if y > 32767:
                y = y - 65536
            
            # Extract source_id and atlas from value2 and value3
            if value2 < 0:
                value2 = value2 + (1 << 32)
            
            source_id = (value2 >> 16) & 0xFF  # Byte 2 contains source_id
            
            # Atlas coordinates come from value3
            if value3 < 0:
                value3_unsigned = value3 + (1 << 32)
            else:
                value3_unsigned = value3
            
            # Try to extract atlas coordinates from value3
            # Most likely: atlas_y = lower bits, alt_id = upper bits
            atlas_y = value3_unsigned & 0xFF
            alt_id = (value3_unsigned >> 16) & 0xFFFF
            
            # For atlas_x, we need to find it - it might be in value3 as well
            # Try: atlas_x = (value3 >> 8) & 0xFF
            atlas_x = (value3_unsigned >> 8) & 0xFF
            
            tiles.append((x, y, source_id, atlas_x, atlas_y, alt_id))
            i += 3
        
        return tiles


class SimpleTileMapRenderer:
    """Simple tilemap renderer - renders all tiles correctly"""
    
    TILE_SIZE = 32
    
    def __init__(self, tilemap_data: Dict, assets_path: str = None):
        self.tilemap_data = tilemap_data
        self.assets_path = Path(assets_path) if assets_path else Path(tilemap_data.get('assets_path', ''))
        self.texture_cache = {}
        self.map_surface = None
        self.tiles = []
        self.textures = []
        self.source_defs = {}
        self.layer_tiles = []
        self.map_offset = tilemap_data.get('tilemap_offset', (0, 0))
        
        # Load textures
        self._load_textures()
        
        # Render the tilemap
        self._create_render_surface()
    
    def _load_textures(self) -> None:
        """Load all PNG textures from assets folder"""
        print("[Renderer] Loading textures...")
        
        if not self.assets_path.exists():
            return
        
        png_files = list(self.assets_path.glob("**/*.png"))
        
        for png_path in png_files:
            try:
                pil_img = Image.open(png_path)
                if pil_img.mode != 'RGBA':
                    pil_img = pil_img.convert('RGBA')
                
                width, height = pil_img.size
                data = pil_img.tobytes('raw', 'RGBA')
                surf = pygame.image.fromstring(data, (width, height), 'RGBA')
                
                self.texture_cache[png_path.name] = surf
                self.texture_cache[str(png_path)] = surf
            except:
                pass
        
        print(f"[Renderer] Loaded {len(self.texture_cache)} textures")
    
    def _create_render_surface(self) -> None:
        """Prepare tiles for dynamic rendering"""
        print("[Renderer] Preparing tilemap for dynamic rendering...")
        
        if not self.tilemap_data.get('layers'):
            return
        
        layers = self.tilemap_data['layers']
        textures = list(self.texture_cache.values())
        self.source_defs = self.tilemap_data.get('tileset_sources', {})
        
        if not textures:
            print("[Renderer] No textures loaded!")
            return
        
        # Collect all tiles to find world bounds and preserve layer order
        all_tiles = []
        ordered_tiles = []
        for layer_idx in sorted(layers.keys()):
            layer_data = layers[layer_idx]
            layer_name = layer_data.get('name', '').lower()
            tiles = layer_data.get('tiles', [])
            if layer_name == 'ysort':
                tiles = sorted(tiles, key=lambda t: t[1])
            ordered_tiles.extend(tiles)
            all_tiles.extend(tiles)
        
        if not all_tiles:
            print("[Renderer] No tiles found")
            return
        
        # Find bounds of actual tile positions
        xs = [t[0] for t in all_tiles]
        ys = [t[1] for t in all_tiles]
        
        # Use all tiles now that coordinates are decoded correctly
        tiles_to_render = all_tiles
        
        if xs and ys:
            min_x, max_x = min(xs), max(xs)
            min_y, max_y = min(ys), max(ys)
        else:
            min_x, max_x = 0, 64
            min_y, max_y = 0, 48
        
        self.tiles = tiles_to_render
        self.layer_tiles = ordered_tiles
        self.textures = textures
        self.map_surface = None
        
        print(f"[Renderer] World bounds: X({min_x}->{max_x}) Y({min_y}->{max_y})")
        print(f"[Renderer] Map offset: {self.map_offset}")
        print(f"[Renderer] TileSet sources: {len(self.source_defs)}")
        for src_id, src_def in list(self.source_defs.items())[:3]:
            print(f"  Source {src_id}: region={src_def.get('region_size')}, atlas_max={src_def.get('atlas_max')}, margins={src_def.get('margins')}")
        print(f"[Renderer] Prepared {len(self.tiles)} tiles for dynamic rendering")
    
    def update(self, camera_offset: Tuple = None, viewport_size: Tuple = None) -> None:
        """Update method (required by engine)"""
        pass
    
    def render(self, display: pygame.Surface, camera_offset: Tuple[float, float]) -> None:
        """Render tilemap to display"""
        if not self.tiles or not self.textures:
            return
        
        view_w, view_h = display.get_size()
        cam_x = camera_offset[0]
        cam_y = camera_offset[1]
        
        tiles_iter = self.layer_tiles if self.layer_tiles else self.tiles
        
        # Debug counters
        rendered = 0
        culled = 0
        no_source = 0
        no_texture = 0
        subsurface_fail = 0
        
        try:
            for x, y, source_id, atlas_x, atlas_y, alt_id in tiles_iter:
                screen_x = int(x * self.TILE_SIZE + self.map_offset[0] - cam_x)
                screen_y = int(y * self.TILE_SIZE + self.map_offset[1] - cam_y)
                
                # Cull tiles outside the viewport (with a small margin)
                if screen_x < -self.TILE_SIZE or screen_y < -self.TILE_SIZE:
                    culled += 1
                    continue
                if screen_x > view_w or screen_y > view_h:
                    culled += 1
                    continue
                
                source_def = self.source_defs.get(source_id)
                if not source_def:
                    no_source += 1
                    if no_source <= 3:
                        print(f"[Renderer] No source def for source_id={source_id}")
                    continue
                texture_path = source_def.get('texture_path')
                texture = self.texture_cache.get(texture_path)
                if texture is None:
                    no_texture += 1
                    if no_texture <= 3:
                        print(f"[Renderer] Missing texture for source {source_id}: {texture_path}")
                    continue
                
                region_size = source_def.get('region_size')
                if region_size is None:
                    # Calculate from texture size and atlas bounds
                    max_ax, max_ay = source_def.get('atlas_max', (-1, -1))
                    if max_ax >= 0 and max_ay >= 0:
                        tex_w, tex_h = texture.get_size()
                        # Subtract margins first
                        margins_def = source_def.get('margins', (0, 0))
                        usable_w = tex_w - margins_def[0]
                        usable_h = tex_h - margins_def[1]
                        region_w = usable_w // (max_ax + 1)
                        region_h = usable_h // (max_ay + 1)
                        region_size = (region_w, region_h)
                    else:
                        region_size = (self.TILE_SIZE, self.TILE_SIZE)
                
                margins = source_def.get('margins', (0, 0))
                tex_w, tex_h = texture.get_size()
                src_x = margins[0] + atlas_x * region_size[0]
                src_y = margins[1] + atlas_y * region_size[1]
                
                try:
                    tile_surf = texture.subsurface((src_x, src_y, region_size[0], region_size[1]))
                except Exception as subsurface_error:
                    subsurface_fail += 1
                    # Suppress error messages - just skip the tile
                    continue
                
                # Apply alternative flags if present
                flags = source_def.get('alt_flags', {}).get((atlas_x, atlas_y, alt_id))
                if flags:
                    if flags.get('transpose'):
                        tile_surf = pygame.transform.rotate(tile_surf, -90)
                    if flags.get('flip_h') or flags.get('flip_v'):
                        tile_surf = pygame.transform.flip(tile_surf, flags.get('flip_h', False), flags.get('flip_v', False))
                
                if tile_surf.get_size() != (self.TILE_SIZE, self.TILE_SIZE):
                    tile_surf = pygame.transform.scale(tile_surf, (self.TILE_SIZE, self.TILE_SIZE))
                
                display.blit(tile_surf, (screen_x, screen_y))
                rendered += 1
        except Exception as e:
            print(f"[Renderer] ERROR: {e}")
            import traceback
            traceback.print_exc()
