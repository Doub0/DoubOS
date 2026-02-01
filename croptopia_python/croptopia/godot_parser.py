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
        """Extract TileMap world offset from node hierarchy"""
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

        # Use JUST the TileMap2's local position as offset (more eastward)
        tilemap_pos = find_node_position('TileMap')
        if tilemap_pos == (0.0, 0.0):
            tilemap_pos = find_node_position('TileMap2')

        self.tilemap_offset = tilemap_pos

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
        pattern = r'\[ext_resource type="Texture2D".*?path="res://([^"]+)".*?id="([^"]+)"\]'

        # Resolve res:// paths from project root (parent of assets/ when available)
        if self.assets_path.name.lower() == "assets":
            project_root = self.assets_path.parent
        else:
            project_root = self.assets_path

        for match in re.finditer(pattern, content):
            rel_path = match.group(1)
            resource_id = match.group(2)
            asset_path = project_root / rel_path

            self.textures[resource_id] = str(asset_path)

        print(f"[Parser] Found {len(self.textures)} texture resources")
    
    def _extract_layer_data(self, content: str) -> None:
        """Extract TileMap layer data"""
        # Try to find TileMap node (could be "TileMap", "TileMap2", etc.)
        tilemap_patterns = [
            r'\[node name="TileMap".*?\n(.*?)\n\[node',  # First try "TileMap"
            r'\[node name="TileMap2".*?\n(.*?)\n\[node',  # Then try "TileMap2"
            r'\[node name="[^"]*TileMap[^"]*".*?\n(.*?)\n\[node'  # Finally try any node with "TileMap"
        ]
        
        tilemap_content = None
        for pattern in tilemap_patterns:
            tilemap_match = re.search(pattern, content, re.DOTALL)
            if tilemap_match:
                tilemap_content = tilemap_match.group(1)
                break
        
        if not tilemap_content:
            print("[Parser] No TileMap found")
            return
        
        # Extract all layer definitions
        layer_pattern = r'layer_(\d+)/name = "([^"]+)"'
        tile_data_pattern = r'layer_(\d+)/tile_data = PackedInt32Array\(([^)]*)\)'
        z_index_pattern = r'layer_(\d+)/z_index = (-?\d+)'
        y_sort_pattern = r'layer_(\d+)/y_sort_enabled = (true|false)'
        
        # Find all layers
        for match in re.finditer(layer_pattern, tilemap_content):
            layer_idx = int(match.group(1))
            layer_name = match.group(2)
            
            # Find tile data for this layer
            tile_match = re.search(f'layer_{layer_idx}/tile_data = PackedInt32Array\\(([^)]*)\\)', tilemap_content)
            
            if tile_match:
                tile_data_str = tile_match.group(1)
                tiles = self._parse_packedint32array(tile_data_str)

                z_index_match = re.search(f'layer_{layer_idx}/z_index = (-?\\d+)', tilemap_content)
                z_index = int(z_index_match.group(1)) if z_index_match else 0

                y_sort_match = re.search(f'layer_{layer_idx}/y_sort_enabled = (true|false)', tilemap_content)
                y_sort_enabled = (y_sort_match.group(1) == 'true') if y_sort_match else False

                self.tilemap_layers[layer_idx] = {
                    'name': layer_name,
                    'tiles': tiles,
                    'z_index': z_index,
                    'y_sort_enabled': y_sort_enabled,
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
        
        # Group into tiles (TileMap format 2):
        # value2 low 16 bits  = source_id (uint16)
        # value2 high 16 bits = atlas_coord_x (uint16)
        # value3 low 16 bits  = atlas_coord_y (uint16)
        # value3 high 16 bits = alternative_tile_id (uint16)
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
            
            source_id = value2 & 0xFFFF
            atlas_x = (value2 >> 16) & 0xFFFF

            if value3 < 0:
                value3 = value3 + (1 << 32)

            atlas_y = value3 & 0xFFFF
            alt_id = (value3 >> 16) & 0xFFFF

            tiles.append((x, y, source_id, atlas_x, atlas_y, alt_id))
            i += 3
        
        return tiles


class SimpleTileMapRenderer:
    """Simple tilemap renderer - renders all tiles correctly"""
    
    TILE_SIZE = 16
    
    def __init__(self, tilemap_data: Dict, assets_path: str = None):
        self.tilemap_data = tilemap_data
        self.assets_path = Path(assets_path) if assets_path else Path(tilemap_data.get('assets_path', ''))
        self.texture_cache = {}
        self.map_surface = None
        self.tiles = []
        self.textures = []
        self.source_defs = {}
        self.layer_tiles = []
        self.layer_order = []  # New: store layer rendering order
        self.map_offset = tilemap_data.get('tilemap_offset', (0, 0))
        
        # Load textures
        self._load_textures()
        
        # Render the tilemap
        self._create_render_surface()
    
    def _load_textures(self) -> None:
        """Load all PNG textures from assets folder"""
        print("[Renderer] Loading textures...")
        
        texture_paths = set()

        if self.assets_path.exists():
            texture_paths.update(self.assets_path.glob("**/*.png"))

        for tex_path in self.tilemap_data.get('textures', {}).values():
            if tex_path:
                texture_paths.add(Path(tex_path))

        for png_path in sorted(texture_paths):
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
        
        # Store layers in render order (sorted by z-index) but keep them separate
        # This preserves per-layer y_sort behavior
        self.layer_order = []
        layer_items = []
        for layer_idx in layers.keys():
            layer_data = layers[layer_idx]
            layer_items.append((
                layer_data.get('z_index', 0),
                layer_idx,
                layer_data
            ))

        all_tiles = []
        for z_index, layer_idx, layer_data in sorted(layer_items, key=lambda item: (item[0], item[1])):
            tiles = layer_data.get('tiles', [])
            
            # Apply y_sort for layers that need it
            if layer_data.get('y_sort_enabled', False):
                tiles = sorted(tiles, key=lambda t: t[1])
            
            # Store this layer for render-time access
            self.layer_order.append((z_index, layer_idx, tiles, layer_data.get('name', 'unnamed')))
            all_tiles.extend(tiles)
        
        if not all_tiles:
            print("[Renderer] No tiles found")
            return
        
        # Find bounds of actual tile positions
        xs = [t[0] for t in all_tiles]
        ys = [t[1] for t in all_tiles]
        
        if xs and ys:
            min_x, max_x = min(xs), max(xs)
            min_y, max_y = min(ys), max(ys)
        else:
            min_x, max_x = 0, 64
            min_y, max_y = 0, 48
        
        self.tiles = all_tiles
        self.layer_tiles = []  # No longer used - we render by layer
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
        """Render tilemap to display, layer by layer in proper z-order"""
        if not self.textures:
            return
        
        view_w, view_h = display.get_size()
        cam_x = camera_offset[0]
        cam_y = camera_offset[1]
        
        # Build spatial grid index for this frame (for efficient lookup)
        self._build_grid_index()
        
        # Render each layer in order
        for z_index, layer_idx, tiles, layer_name in self.layer_order:
            self._render_layer(display, tiles, camera_offset, layer_name)
    
    def _build_grid_index(self) -> None:
        """Build a spatial grid index of tiles by position for fast lookup"""
        self.grid_index = {}  # {(x, y): [(layer_idx, tile_data), ...]}
        
        for z_index, layer_idx, tiles, layer_name in self.layer_order:
            for tile in tiles:
                x, y = tile[0], tile[1]
                grid_pos = (x, y)
                
                if grid_pos not in self.grid_index:
                    self.grid_index[grid_pos] = []
                
                self.grid_index[grid_pos].append((layer_idx, tile))
    
    def _render_layer(self, display: pygame.Surface, tiles: list, camera_offset: Tuple[float, float], layer_name: str) -> None:
        """Render a single layer of tiles by scanning the tilemap grid"""
        if not tiles or not self.textures:
            return
        
        view_w, view_h = display.get_size()
        cam_x = camera_offset[0]
        cam_y = camera_offset[1]
        
        rendered = 0
        culled = 0
        skipped = 0
        
        try:
            for tile in tiles:
                if len(tile) == 6:
                    x, y, source_id, atlas_x, atlas_y, alt_id = tile
                else:
                    x, y, source_id, atlas_index, alt_id = tile
                    atlas_x, atlas_y = 0, 0
                
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
                    skipped += 1
                    continue
                if len(tile) == 5:
                    atlas_coords_list = source_def.get('atlas_coords_list', [])
                    max_ax, max_ay = source_def.get('atlas_max', (-1, -1))
                    
                    if atlas_coords_list:
                        # Source has manually-defined atlas coordinates
                        # Wrap index using modulo to fit within available coords
                        wrapped_idx = atlas_index % len(atlas_coords_list)
                        atlas_x, atlas_y = atlas_coords_list[wrapped_idx]
                    elif max_ax >= 0 and max_ay >= 0:
                        # Regular grid source - use linear index
                        cols = max_ax + 1
                        atlas_x = atlas_index % cols
                        atlas_y = atlas_index // cols
                        
                        # Bounds check: if calculated Y is out of range, skip this tile
                        if atlas_y > max_ay:
                            skipped += 1
                            continue
                    else:
                        skipped += 1
                        continue
                texture_path = source_def.get('texture_path')
                texture = self.texture_cache.get(texture_path)
                if texture is None:
                    skipped += 1
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
                    skipped += 1
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
            print(f"[Renderer] ERROR in {layer_name}: {e}")
            import traceback
            traceback.print_exc()
