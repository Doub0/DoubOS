"""
Entity Manager - Loads and renders all game objects/entities
Parses scene instances from spawn_node.tscn and renders them
"""

import pygame
import os
import re
from typing import List, Dict, Tuple, Optional, Callable


class Entity:
    """Represents a game object/entity"""
    
    def __init__(self, name: str, scene_path: str, position: Tuple[float, float],
                 scale: Tuple[float, float] = (1.0, 1.0), visible: bool = True,
                 scene_tag: Optional[str] = None, z_index: int = 0):
        self.name = name
        self.scene_path = scene_path
        self.position = position
        self.scale = scale
        self.visible = visible
        self.scene_tag = scene_tag
        self.z_index = z_index
        self.sprite: Optional[pygame.Surface] = None
        self.sprite_parts: List[Tuple[pygame.Surface, Tuple[float, float], Tuple[float, float]]] = []
        self.animation = "default"  # Current animation frame
        self.collectable = self._is_collectable()  # Check if entity can be collected
        self.collection_radius = 30.0  # Pixels within which player can collect
        
    def _is_collectable(self) -> bool:
        """Determine if entity is collectable based on scene name."""
        collectable_types = [
            "shrub", "pinecone", "stick", "sorrel", "chive", 
            "redbaneberry", "elderberry", "collectable"
        ]
        scene_name = self.scene_path.lower()
        return any(ctype in scene_name for ctype in collectable_types)
    
    def get_item_type(self) -> str:
        """Get the item type name for quest tracking."""
        scene_name = self.scene_path.lower()
        
        # Map scene names to item types
        if "pinecone" in scene_name or "shrub" in scene_name:
            return "pinecone"
        elif "stick" in scene_name:
            return "stick"
        elif "sorrel" in scene_name:
            return "sorrel"
        elif "redbaneberry" in scene_name or "redbane" in scene_name:
            return "redbaneberry"
        elif "chive" in scene_name:
            return "chives"
        elif "elderberry" in scene_name:
            return "elderberry"
        
        return "unknown"
        
    def __repr__(self):
        return f"Entity({self.name}, {self.scene_path}, pos={self.position}, z={self.z_index}, visible={self.visible})"


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
        self.scene_z_index: Dict[str, int] = {}  # Cache z-index per scene
        self.collection_callback: Optional[Callable] = None  # Callback for entity collection
        
        print(f"[EntityManager] Initializing...")
        self._parse_entities()
        self._load_entity_sprites()
        print(f"[EntityManager] Loaded {len(self.entities)} entities")
    
    def set_collection_callback(self, callback: Callable[[str], None]):
        """Set callback function for when entities are collected."""
        self.collection_callback = callback
        
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
            
            # Match entity node declaration (spawn, spawn/objects, spawn/entities, spawn/out_of_bounds)
            node_match = re.match(r'\[node name="(.*?)" parent="spawn(/[\w_]+|)" instance=ExtResource\("(\d+_\w+)"\)\]', line)
            
            if node_match:
                entity_name = node_match.group(1)
                resource_id = node_match.group(3)  # group(3) is now the resource ID
                
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
                entity = Entity(entity_name, scene_path, position, scale, visible, scene_tag="spawn_node")
                self.entities.append(entity)
                
                i = j
            else:
                i += 1
    
    def _load_entity_sprites(self):
        """Load sprite textures for each entity type"""
        self._load_entity_sprites_for_scene_paths(
            set(entity.scene_path for entity in self.entities)
        )

    def _load_entity_sprites_for_scene_paths(self, scenes_to_load: set):
        """Load sprite textures for a specific set of scene paths."""
        if not scenes_to_load:
            return

        # Only load scenes not already cached
        scenes_to_load = {s for s in scenes_to_load if s not in self.scene_sprites}
        if not scenes_to_load:
            return

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
            sprite_parts, scene_z_index = self._extract_sprite_parts_from_scene(full_scene_path)

            if scene_z_index is not None:
                self.scene_z_index[scene_path] = scene_z_index

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
                                loaded_parts.append((
                                    sprite,
                                    part["offset"],
                                    part["scale"],
                                    part["z_index"],
                                    part["order"],
                                ))
                                break
                            except Exception as e:
                                print(f"[EntityManager] ERROR loading {full_texture_path}: {e}")

                if loaded_parts:
                    loaded_parts.sort(key=lambda p: (p[3], p[4]))
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
        
        # Assign sprites and z-index to entities
        for entity in self.entities:
            if entity.scene_path in self.scene_sprites:
                sprite_data = self.scene_sprites[entity.scene_path]
                if isinstance(sprite_data, list):
                    entity.sprite_parts = sprite_data
                else:
                    entity.sprite = sprite_data

            if entity.scene_path in self.scene_z_index:
                entity.z_index = self.scene_z_index[entity.scene_path]

    def add_scene_entities(self, scene_tscn_path: str, scene_offset: Tuple[float, float] = (0.0, 0.0), scene_tag: Optional[str] = None):
        """
        Parse and add ALL instance nodes from a scene .tscn, applying a world offset.
        This ensures every single child instance is added, including those under nested parents.
        """
        if not os.path.exists(scene_tscn_path):
            print(f"[EntityManager] Scene not found: {scene_tscn_path}")
            return 0

        with open(scene_tscn_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Map ExtResource IDs to scene paths
        ext_resources = {}
        for match in re.finditer(r'\[ext_resource type="PackedScene".*?path="(.*?)".*?id="(\d+_\w+)"\]', content):
            path = match.group(1).replace('res://', '')
            resource_id = match.group(2)
            ext_resources[resource_id] = path

        # First pass: collect node parents + local positions
        node_parents: Dict[str, Optional[str]] = {}
        node_positions: Dict[str, Tuple[float, float]] = {}

        node_header_pattern = re.compile(r'\[node name="(.*?)"(?:[^\]]*?) parent="(.*?)"[^\]]*\]')
        lines = content.split('\n')
        i = 0
        while i < len(lines):
            line = lines[i]
            header_match = node_header_pattern.match(line)
            if header_match:
                name = header_match.group(1)
                parent = header_match.group(2)
                parent_path = None if parent == "." else parent
                full_path = name if parent == "." else f"{parent}/{name}"
                node_parents[full_path] = parent_path

                local_pos = (0.0, 0.0)
                j = i + 1
                while j < len(lines) and not lines[j].startswith('['):
                    prop_line = lines[j].strip()
                    pos_match = re.match(r'position = Vector2\(([-\d.]+), ([-\d.]+)\)', prop_line)
                    if pos_match:
                        local_pos = (float(pos_match.group(1)), float(pos_match.group(2)))
                    j += 1

                node_positions[full_path] = local_pos
                i = j
            else:
                i += 1

        def resolve_world_pos(full_path: str) -> Tuple[float, float]:
            """Resolve world position by summing parent transforms."""
            total_x, total_y = node_positions.get(full_path, (0.0, 0.0))
            parent_path = node_parents.get(full_path)
            while parent_path:
                parent_pos = node_positions.get(parent_path, (0.0, 0.0))
                total_x += parent_pos[0]
                total_y += parent_pos[1]
                parent_path = node_parents.get(parent_path)
            return (total_x, total_y)

        # Second pass: add ALL instance nodes
        added_entities = 0
        i = 0
        while i < len(lines):
            line = lines[i]
            if line.startswith('[node') and 'instance=ExtResource(' in line:
                name_match = re.search(r'name="(.*?)"', line)
                parent_match = re.search(r'parent="(.*?)"', line)
                inst_match = re.search(r'instance=ExtResource\("(\d+_\w+)"\)', line)

                if not name_match or not inst_match:
                    i += 1
                    continue

                entity_name = name_match.group(1)
                parent = parent_match.group(1) if parent_match else "."
                resource_id = inst_match.group(1)

                if resource_id not in ext_resources:
                    i += 1
                    continue

                scene_path = ext_resources[resource_id]

                full_path = entity_name if parent == "." else f"{parent}/{entity_name}"
                base_pos = resolve_world_pos(full_path)
                position = (base_pos[0] + scene_offset[0], base_pos[1] + scene_offset[1])

                scale = (1.0, 1.0)
                visible = True

                j = i + 1
                while j < len(lines) and not lines[j].startswith('['):
                    prop_line = lines[j].strip()
                    scale_match = re.match(r'scale = Vector2\(([-\d.]+), ([-\d.]+)\)', prop_line)
                    if scale_match:
                        scale = (float(scale_match.group(1)), float(scale_match.group(2)))

                    if prop_line == 'visible = false':
                        visible = False
                    j += 1

                entity = Entity(entity_name, scene_path, position, scale, visible, scene_tag=scene_tag)
                self.entities.append(entity)
                added_entities += 1

                i = j
            else:
                i += 1

        # Load sprites for newly added entities only
        self._load_entity_sprites_for_scene_paths(
            {e.scene_path for e in self.entities[-added_entities:]}
        )

        print(f"[EntityManager] Added {added_entities} entities from {os.path.basename(scene_tscn_path)}")
        return added_entities

    def check_collection_nearby(self, player_position: pygame.Vector2, entity_indices: set) -> Optional[str]:
        """Check if player is near collectable entities within a subset of indices."""
        for idx in entity_indices:
            if idx >= len(self.entities):
                continue
            entity = self.entities[idx]
            if not entity.visible or not entity.collectable:
                continue

            entity_pos = pygame.Vector2(entity.position)
            distance = player_position.distance_to(entity_pos)

            if distance < entity.collection_radius:
                entity.visible = False
                item_type = entity.get_item_type()

                if self.collection_callback:
                    self.collection_callback(item_type)

                print(f"[EntityManager] Collected: {item_type} ({entity.name})")
                return item_type

        return None
    
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

    def _extract_sprite_parts_from_scene(self, scene_file_path: str) -> Tuple[List[Dict], Optional[int]]:
        """Extract all Sprite2D/AnimatedSprite2D parts with offsets, scales, and z-index."""
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

            # Find root z-index (parent=".")
            root_z_index = 0
            root_found = False

            lines = content.split('\n')
            i = 0
            while i < len(lines):
                line = lines[i]
                root_match = re.match(r'\[node name="(.*?)".*?parent="\."', line)
                if root_match:
                    root_found = True
                    j = i + 1
                    while j < len(lines) and not lines[j].startswith('['):
                        prop_line = lines[j].strip()
                        z_match = re.match(r'z_index = (-?\d+)', prop_line)
                        if z_match:
                            root_z_index = int(z_match.group(1))
                        j += 1
                    break
                i += 1

            parts = []
            i = 0
            order_index = 0
            while i < len(lines):
                line = lines[i]
                node_match = re.match(r'\[node name="(.*?)" type="(Sprite2D|AnimatedSprite2D)"', line)
                if node_match:
                    position = (0.0, 0.0)
                    scale = (1.0, 1.0)
                    texture_path = None
                    spriteframes_id = None
                    z_index = 0
                    z_as_relative = True

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

                        z_match = re.match(r'z_index = (-?\d+)', prop_line)
                        if z_match:
                            z_index = int(z_match.group(1))

                        z_rel_match = re.match(r'z_as_relative = (true|false)', prop_line)
                        if z_rel_match:
                            z_as_relative = (z_rel_match.group(1) == 'true')

                        j += 1

                    if not texture_path and spriteframes_id:
                        texture_path = resolve_spriteframes_texture(spriteframes_id)

                    if texture_path:
                        effective_z = z_index + root_z_index if z_as_relative else z_index
                        parts.append({
                            "texture_path": texture_path,
                            "offset": position,
                            "scale": scale,
                            "z_index": effective_z,
                            "order": order_index
                        })
                        order_index += 1

                    i = j
                else:
                    i += 1

            return parts, (root_z_index if root_found else None)
        except Exception as e:
            print(f"[EntityManager] ERROR extracting sprite parts from {scene_file_path}: {e}")
            return [], None
    
    def render(self, surface: pygame.Surface, camera_offset: Tuple[int, int]):
        """
        Render all visible entities
        
        Args:
            surface: Pygame surface to render to
            camera_offset: (x, y) camera offset for scrolling
        """
        
        return self.render_scene_tags(surface, camera_offset, None)

    def render_scene_tags(self, surface: pygame.Surface, camera_offset: Tuple[int, int], scene_tags: Optional[set]):
        """
        Render only entities matching scene tags (or all if scene_tags is None).

        Args:
            surface: Pygame surface to render to
            camera_offset: (x, y) camera offset for scrolling
            scene_tags: set of scene tags to render, or None for all
        """
        rendered_count = 0

        if scene_tags is None:
            draw_list = [e for e in self.entities if e.visible]
        else:
            draw_list = [e for e in self.entities if e.visible and getattr(e, "scene_tag", None) in scene_tags]

        draw_list.sort(key=lambda e: (e.z_index, e.position[1], e.position[0]))

        for entity in draw_list:
            if not entity.visible:
                continue

            screen_x = entity.position[0] - camera_offset[0]
            screen_y = entity.position[1] - camera_offset[1]

            if entity.sprite_parts:
                for sprite, offset, scale, z_index, order in entity.sprite_parts:
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

    
    def check_collection(self, player_position: pygame.Vector2) -> Optional[str]:
        """
        Check if player is near a collectable entity.
        Returns item type if entity collected, None otherwise.
        """
        for entity in self.entities:
            if not entity.visible or not entity.collectable:
                continue
            
            # Calculate distance to player
            entity_pos = pygame.Vector2(entity.position)
            distance = player_position.distance_to(entity_pos)
            
            if distance < entity.collection_radius:
                # Collect the entity
                entity.visible = False
                item_type = entity.get_item_type()
                
                # Trigger callback if set
                if self.collection_callback:
                    self.collection_callback(item_type)
                
                print(f"[EntityManager] Collected: {item_type} ({entity.name})")
                return item_type
        
        return None
    
    def get_nearby_collectable(self, player_position: pygame.Vector2, radius: float = 40.0) -> Optional[Entity]:
        """Get nearest collectable entity within radius."""
        nearest = None
        nearest_dist = radius
        
        for entity in self.entities:
            if not entity.visible or not entity.collectable:
                continue
            
            entity_pos = pygame.Vector2(entity.position)
            distance = player_position.distance_to(entity_pos)
            
            if distance < nearest_dist:
                nearest = entity
                nearest_dist = distance
        
        return nearest
