"""
Entity Manager - Loads and renders all game objects/entities
Parses scene instances from spawn_node.tscn and renders them
"""

import pygame
import os
import re
from typing import List, Dict, Tuple, Optional


class Entity:
    """Represents a game object/entity"""
    
    def __init__(self, name: str, scene_path: str, position: Tuple[float, float], 
                 scale: Tuple[float, float] = (1.0, 1.0), visible: bool = True):
        self.name = name
        self.scene_path = scene_path
        self.position = position
        self.scale = scale
        self.visible = visible
        self.sprite: Optional[pygame.Surface] = None
        self.sprite_parts: List[Tuple[pygame.Surface, Tuple[float, float], Tuple[float, float]]] = []
        self.animation = "default"  # Current animation frame
        
    def __repr__(self):
        return f"Entity({self.name}, {self.scene_path}, pos={self.position}, visible={self.visible})"


class EntityManager:
    """
    Manages all game entities/objects
    - Parses entity instances from spawn_node.tscn
    - Loads sprite data from scene files
    - Renders entities on screen
    """
    
    def __init__(self, spawn_tscn_path: str, assets_path: str):
        self.spawn_tscn_path = spawn_tscn_path
        self.assets_path = assets_path
        self.entities: List[Entity] = []
        self.scene_sprites: Dict[str, pygame.Surface] = {}  # Cache loaded sprites
        
        print(f"[EntityManager] Initializing...")
        self._parse_entities()
        self._load_entity_sprites()
        print(f"[EntityManager] Loaded {len(self.entities)} entities")
        
    def _parse_entities(self):
        """Parse all entity instances from spawn_node.tscn"""
        
        with open(self.spawn_tscn_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # First, extract ExtResource mappings (id -> path)
        ext_resources = {}
        for match in re.finditer(r'\[ext_resource type="PackedScene".*?path="(.*?)".*?id="(\d+_\w+)"\]', content):
            path = match.group(1).replace('res://', '')
            resource_id = match.group(2)
            ext_resources[resource_id] = path
        
        print(f"[EntityManager] Found {len(ext_resources)} scene resources")
        
        # Parse entity node instances
        # Pattern: [node name="entity_name" parent="spawn/objects" instance=ExtResource("id")]
        #          position = Vector2(x, y)
        #          scale = Vector2(sx, sy)  [optional]
        #          visible = false  [optional]
        
        lines = content.split('\n')
        i = 0
        while i < len(lines):
            line = lines[i]
            
            # Match entity node declaration
            node_match = re.match(r'\[node name="(.*?)" parent="spawn/(objects|entities)" instance=ExtResource\("(\d+_\w+)"\)\]', line)
            
            if node_match:
                entity_name = node_match.group(1)
                resource_id = node_match.group(3)
                
                # Get scene path from resource mapping
                if resource_id not in ext_resources:
                    i += 1
                    continue
                    
                scene_path = ext_resources[resource_id]
                
                # Parse properties from following lines
                position = (0.0, 0.0)
                scale = (1.0, 1.0)
                visible = True
                
                # Look ahead for properties
                j = i + 1
                while j < len(lines) and not lines[j].startswith('['):
                    prop_line = lines[j].strip()
                    
                    # Parse position
                    pos_match = re.match(r'position = Vector2\(([-\d.]+), ([-\d.]+)\)', prop_line)
                    if pos_match:
                        position = (float(pos_match.group(1)), float(pos_match.group(2)))
                    
                    # Parse scale
                    scale_match = re.match(r'scale = Vector2\(([-\d.]+), ([-\d.]+)\)', prop_line)
                    if scale_match:
                        scale = (float(scale_match.group(1)), float(scale_match.group(2)))
                    
                    # Parse visibility
                    if prop_line == 'visible = false':
                        visible = False
                    
                    j += 1
                
                # Create entity
                entity = Entity(entity_name, scene_path, position, scale, visible)
                self.entities.append(entity)
                
                i = j
            else:
                i += 1
    
    def _load_entity_sprites(self):
        """Load sprite textures for each entity type"""
        
        # Group entities by scene to avoid loading same texture multiple times
        scenes_to_load = set(entity.scene_path for entity in self.entities)
        
        print(f"[EntityManager] Loading sprites for {len(scenes_to_load)} unique scene types...")
        
        for scene_path in scenes_to_load:
            # Construct full path to scene file
            full_scene_path = os.path.join(os.path.dirname(self.spawn_tscn_path), "..", scene_path)
            full_scene_path = os.path.normpath(full_scene_path)
            
            if not os.path.exists(full_scene_path):
                # Try alternate location
                full_scene_path = os.path.join(os.path.dirname(self.spawn_tscn_path), scene_path)
                full_scene_path = os.path.normpath(full_scene_path)
            
            if not os.path.exists(full_scene_path):
                print(f"[EntityManager] WARNING: Scene file not found: {scene_path}")
                continue
            
            # Parse scene file to extract sprite parts
            sprite_parts = self._extract_sprite_parts_from_scene(full_scene_path)

            if sprite_parts:
                loaded_parts = []
                for part in sprite_parts:
                    texture_path = part["texture_path"].replace('assets/', '')
                    texture_locations = [
                        os.path.join(self.assets_path, texture_path),
                        os.path.join(os.path.dirname(self.assets_path), texture_path),
                    ]

                    for full_texture_path in texture_locations:
                        if os.path.exists(full_texture_path):
                            try:
                                sprite = pygame.image.load(full_texture_path).convert_alpha()
                                loaded_parts.append((sprite, part["offset"], part["scale"]))
                                break
                            except Exception as e:
                                print(f"[EntityManager] ERROR loading {full_texture_path}: {e}")

                if loaded_parts:
                    self.scene_sprites[scene_path] = loaded_parts
                    print(f"[EntityManager] Loaded {len(loaded_parts)} sprite parts for {os.path.basename(scene_path)}")
                    continue

            # Fallback: single texture extraction
            texture_path = self._extract_texture_from_scene(full_scene_path)

            if texture_path:
                texture_path = texture_path.replace('assets/', '')
                texture_locations = [
                    os.path.join(self.assets_path, texture_path),
                    os.path.join(os.path.dirname(self.assets_path), texture_path),
                ]

                loaded = False
                for full_texture_path in texture_locations:
                    if os.path.exists(full_texture_path):
                        try:
                            sprite = pygame.image.load(full_texture_path).convert_alpha()
                            self.scene_sprites[scene_path] = sprite
                            print(f"[EntityManager] Loaded sprite for {os.path.basename(scene_path)}: {texture_path}")
                            loaded = True
                            break
                        except Exception as e:
                            print(f"[EntityManager] ERROR loading {full_texture_path}: {e}")

                if not loaded:
                    print(f"[EntityManager] WARNING: Texture not found in any location: {texture_path}")
        
        # Assign sprites to entities
        for entity in self.entities:
            if entity.scene_path in self.scene_sprites:
                sprite_data = self.scene_sprites[entity.scene_path]
                if isinstance(sprite_data, list):
                    entity.sprite_parts = sprite_data
                else:
                    entity.sprite = sprite_data
    
    def _extract_texture_from_scene(self, scene_file_path: str) -> Optional[str]:
        """Extract the primary texture path from a scene file"""
        
        try:
            with open(scene_file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Look for texture resource
            # Pattern: [ext_resource type="Texture2D" ... path="res://path/to/texture.png" ...]
            texture_match = re.search(r'\[ext_resource type="Texture2D".*?path="res://(.*?\.png)"', content)
            
            if texture_match:
                return texture_match.group(1)
            
            # Alternate pattern: Look for direct texture assignment
            texture_match = re.search(r'texture = ExtResource\("(\d+_\w+)"\)', content)
            if texture_match:
                resource_id = texture_match.group(1)
                # Find the resource definition
                resource_match = re.search(rf'\[ext_resource.*?path="res://(.*?\.png)".*?id="{resource_id}"\]', content)
                if resource_match:
                    return resource_match.group(1)
            
            return None
            
        except Exception as e:
            print(f"[EntityManager] ERROR parsing scene {scene_file_path}: {e}")
            return None

    def _extract_sprite_parts_from_scene(self, scene_file_path: str) -> List[Dict]:
        """Extract all Sprite2D/AnimatedSprite2D parts with offsets and scales."""
        try:
            with open(scene_file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            ext_resources = {}
            for match in re.finditer(r'\[ext_resource type="Texture2D".*?path="res://(.*?)".*?id="(\d+_\w+)"\]', content):
                ext_resources[match.group(2)] = match.group(1)

            def get_subresource_block(sub_id: str) -> str:
                pattern = rf'\[sub_resource[^\]]*id="{re.escape(sub_id)}"\](.*?)(?=\n\[sub_resource|\n\[node|\Z)'
                match = re.search(pattern, content, re.S)
                return match.group(1) if match else ""

            def resolve_spriteframes_texture(spriteframes_id: str) -> Optional[str]:
                block = get_subresource_block(spriteframes_id)
                if not block:
                    return None

                # Look for direct texture references
                ext_match = re.search(r'ExtResource\("(\d+_\w+)"\)', block)
                if ext_match:
                    tex_id = ext_match.group(1)
                    return ext_resources.get(tex_id)

                # Look for atlas subresource
                sub_match = re.search(r'SubResource\("(\w+_\w+)"\)', block)
                if sub_match:
                    atlas_id = sub_match.group(1)
                    atlas_block = get_subresource_block(atlas_id)
                    atlas_ext = re.search(r'atlas = ExtResource\("(\d+_\w+)"\)', atlas_block)
                    if atlas_ext:
                        return ext_resources.get(atlas_ext.group(1))

                return None

            parts = []
            lines = content.split('\n')
            i = 0
            while i < len(lines):
                line = lines[i]
                node_match = re.match(r'\[node name="(.*?)" type="(Sprite2D|AnimatedSprite2D)"', line)
                if node_match:
                    position = (0.0, 0.0)
                    scale = (1.0, 1.0)
                    texture_path = None
                    spriteframes_id = None

                    j = i + 1
                    while j < len(lines) and not lines[j].startswith('['):
                        prop_line = lines[j].strip()
                        pos_match = re.match(r'position = Vector2\(([-\d.]+), ([-\d.]+)\)', prop_line)
                        if pos_match:
                            position = (float(pos_match.group(1)), float(pos_match.group(2)))

                        scale_match = re.match(r'scale = Vector2\(([-\d.]+), ([-\d.]+)\)', prop_line)
                        if scale_match:
                            scale = (float(scale_match.group(1)), float(scale_match.group(2)))

                        tex_match = re.match(r'texture = ExtResource\("(\d+_\w+)"\)', prop_line)
                        if tex_match:
                            texture_path = ext_resources.get(tex_match.group(1))

                        frames_match = re.match(r'sprite_frames = SubResource\("(\w+_\w+)"\)', prop_line)
                        if frames_match:
                            spriteframes_id = frames_match.group(1)

                        j += 1

                    if not texture_path and spriteframes_id:
                        texture_path = resolve_spriteframes_texture(spriteframes_id)

                    if texture_path:
                        parts.append({
                            "texture_path": texture_path,
                            "offset": position,
                            "scale": scale
                        })

                    i = j
                else:
                    i += 1

            return parts
        except Exception as e:
            print(f"[EntityManager] ERROR extracting sprite parts from {scene_file_path}: {e}")
            return []
    
    def render(self, surface: pygame.Surface, camera_offset: Tuple[int, int]):
        """
        Render all visible entities
        
        Args:
            surface: Pygame surface to render to
            camera_offset: (x, y) camera offset for scrolling
        """
        
        rendered_count = 0
        
        for entity in self.entities:
            if not entity.visible:
                continue

            screen_x = entity.position[0] - camera_offset[0]
            screen_y = entity.position[1] - camera_offset[1]

            if entity.sprite_parts:
                for sprite, offset, scale in entity.sprite_parts:
                    combined_scale = (entity.scale[0] * scale[0], entity.scale[1] * scale[1])
                    scaled_w = int(sprite.get_width() * combined_scale[0])
                    scaled_h = int(sprite.get_height() * combined_scale[1])
                    scaled_sprite = pygame.transform.scale(sprite, (scaled_w, scaled_h))

                    part_x = screen_x + offset[0]
                    part_y = screen_y + offset[1]
                    render_x = part_x - scaled_sprite.get_width() // 2
                    render_y = part_y - scaled_sprite.get_height() // 2

                    if (render_x + scaled_sprite.get_width() < 0 or 
                        render_x > surface.get_width() or
                        render_y + scaled_sprite.get_height() < 0 or
                        render_y > surface.get_height()):
                        continue

                    surface.blit(scaled_sprite, (render_x, render_y))
                    rendered_count += 1
                continue

            if entity.sprite is None:
                continue

            if entity.scale != (1.0, 1.0):
                scaled_w = int(entity.sprite.get_width() * entity.scale[0])
                scaled_h = int(entity.sprite.get_height() * entity.scale[1])
                scaled_sprite = pygame.transform.scale(entity.sprite, (scaled_w, scaled_h))
            else:
                scaled_sprite = entity.sprite

            render_x = screen_x - scaled_sprite.get_width() // 2
            render_y = screen_y - scaled_sprite.get_height() // 2

            if (render_x + scaled_sprite.get_width() < 0 or 
                render_x > surface.get_width() or
                render_y + scaled_sprite.get_height() < 0 or
                render_y > surface.get_height()):
                continue

            surface.blit(scaled_sprite, (render_x, render_y))
            rendered_count += 1
        
        return rendered_count
    
    def get_entity_count(self) -> int:
        """Get total number of entities"""
        return len(self.entities)
    
    def get_visible_entity_count(self) -> int:
        """Get number of visible entities"""
        return sum(1 for e in self.entities if e.visible)
