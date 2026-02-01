"""
Entity Level-of-Detail (LOD) System
Optimizes rendering by using spatial partitioning and multi-tier LOD

Key Features:
- Spatial grid for fast entity lookup (only check nearby entities)
- Distance-based LOD: Near (full detail) -> Medium (reduced) -> Far (minimal/culled)
- Background processing: Entities update on low-priority timers when off-screen
- Frame budget: Only render X entities per frame to prevent lag spikes
"""

import pygame
from typing import List, Dict, Tuple, Set, Optional
from collections import defaultdict
import time


class EntityLOD:
    """Represents different rendering quality levels for an entity"""
    FULL = 0      # Full detail, all sprite parts, full scale
    REDUCED = 1   # Simplified rendering, single sprite, reduced scale  
    MINIMAL = 2   # Tiny billboard or single pixel
    CULLED = 3    # Not rendered at all, but still processing
    

class SpatialGrid:
    """
    Spatial partitioning grid for fast entity lookup.
    Divides world into cells for O(1) nearby entity queries.
    """
    
    def __init__(self, cell_size: int = 512):
        """
        Args:
            cell_size: Size of each grid cell in pixels (larger = fewer cells, more entities per cell)
        """
        self.cell_size = cell_size
        self.grid: Dict[Tuple[int, int], Set[int]] = defaultdict(set)  # (cell_x, cell_y) -> set of entity indices
        
    def _get_cell(self, x: float, y: float) -> Tuple[int, int]:
        """Convert world position to grid cell coordinates"""
        return (int(x // self.cell_size), int(y // self.cell_size))
    
    def add_entity(self, entity_id: int, position: Tuple[float, float]):
        """Add entity to grid"""
        cell = self._get_cell(position[0], position[1])
        self.grid[cell].add(entity_id)
    
    def remove_entity(self, entity_id: int, position: Tuple[float, float]):
        """Remove entity from grid"""
        cell = self._get_cell(position[0], position[1])
        self.grid[cell].discard(entity_id)
    
    def get_nearby_entities(self, position: Tuple[float, float], radius_cells: int = 2) -> Set[int]:
        """
        Get all entity IDs near a position.
        
        Args:
            position: World position to check
            radius_cells: Number of cells to check in each direction (2 = 5x5 grid)
        """
        center_cell = self._get_cell(position[0], position[1])
        nearby = set()
        
        for dx in range(-radius_cells, radius_cells + 1):
            for dy in range(-radius_cells, radius_cells + 1):
                cell = (center_cell[0] + dx, center_cell[1] + dy)
                nearby.update(self.grid.get(cell, set()))
        
        return nearby
    
    def clear(self):
        """Clear all entities from grid"""
        self.grid.clear()


class EntityLODManager:
    """
    Manages entity rendering with LOD system.
    Reduces lag by:
    1. Only rendering nearby entities
    2. Using simplified rendering for distant entities
    3. Frame budget limiting (max entities rendered per frame)
    4. Spatial partitioning for fast queries
    """
    
    def __init__(self, entities: List, lod_distances: Dict[int, float] = None, max_per_frame: int = 200):
        """
        Args:
            entities: List of Entity objects to manage
            lod_distances: Dict mapping LOD level to max distance in pixels
                          Default: {FULL: 400, REDUCED: 800, MINIMAL: 1200, CULLED: infinity}
            max_per_frame: Maximum entities to render per frame (frame budget)
        """
        self.entities = entities
        self.spatial_grid = SpatialGrid(cell_size=512)
        self.max_per_frame = max_per_frame
        
        # LOD distance thresholds (squared for faster comparison)
        self.lod_distances_sq = lod_distances or {
            EntityLOD.FULL: 800 ** 2,      # 800px radius
            EntityLOD.REDUCED: 1600 ** 2,  # 1600px radius
            EntityLOD.MINIMAL: 3200 ** 2,  # 3200px radius
        }
        
        # Cache for pre-rendered simplified sprites
        self.reduced_sprite_cache: Dict[int, pygame.Surface] = {}
        self.minimal_sprite_cache: Dict[int, pygame.Surface] = {}
        
        # Build spatial grid
        self._rebuild_spatial_grid()
        
        # Background processing timer
        self.last_background_update = time.time()
        self.background_update_interval = 0.5  # Update off-screen entities every 0.5s
        
    def _rebuild_spatial_grid(self):
        """Rebuild the spatial partitioning grid"""
        self.spatial_grid.clear()
        for idx, entity in enumerate(self.entities):
            if entity.visible:
                self.spatial_grid.add_entity(idx, entity.position)

    def rebuild_spatial_grid(self):
        """Public wrapper to rebuild spatial grid after entities change."""
        self._rebuild_spatial_grid()

    def get_nearby_entity_indices(self, position: Tuple[float, float], radius_cells: int = 1) -> Set[int]:
        """Get nearby entity indices using spatial grid."""
        return self.spatial_grid.get_nearby_entities(position, radius_cells=radius_cells)
    
    def _get_lod_level(self, distance_sq: float) -> int:
        """Determine LOD level based on squared distance"""
        if distance_sq < self.lod_distances_sq[EntityLOD.FULL]:
            return EntityLOD.FULL
        elif distance_sq < self.lod_distances_sq[EntityLOD.REDUCED]:
            return EntityLOD.REDUCED
        elif distance_sq < self.lod_distances_sq[EntityLOD.MINIMAL]:
            return EntityLOD.MINIMAL
        else:
            return EntityLOD.CULLED
    
    def _get_reduced_sprite(self, entity, entity_idx: int) -> pygame.Surface:
        """Get or create reduced quality sprite for entity"""
        if entity_idx in self.reduced_sprite_cache:
            return self.reduced_sprite_cache[entity_idx]
        
        # Create reduced sprite (50% scale, single texture)
        if entity.sprite_parts:
            # Use first sprite part only
            sprite, offset, scale, z_index, order = entity.sprite_parts[0]
            reduced = pygame.transform.scale(sprite, (sprite.get_width() // 2, sprite.get_height() // 2))
        elif entity.sprite:
            reduced = pygame.transform.scale(entity.sprite, (entity.sprite.get_width() // 2, entity.sprite.get_height() // 2))
        else:
            # Fallback: 8x8 colored square
            reduced = pygame.Surface((8, 8))
            reduced.fill((100, 200, 100))
        
        self.reduced_sprite_cache[entity_idx] = reduced
        return reduced
    
    def _get_minimal_sprite(self, entity, entity_idx: int) -> pygame.Surface:
        """Get or create minimal quality sprite (tiny billboard)"""
        if entity_idx in self.minimal_sprite_cache:
            return self.minimal_sprite_cache[entity_idx]
        
        # Create 4x4 colored pixel
        minimal = pygame.Surface((4, 4))
        
        # Color based on entity type
        scene_name = entity.scene_path.lower()
        if "tree" in scene_name:
            color = (50, 150, 50)  # Green
        elif "bush" in scene_name or "shrub" in scene_name:
            color = (100, 200, 100)  # Light green
        elif "stick" in scene_name:
            color = (139, 69, 19)  # Brown
        else:
            color = (200, 200, 200)  # Gray
        
        minimal.fill(color)
        self.minimal_sprite_cache[entity_idx] = minimal
        return minimal
    
    def _render_entity_full(self, surface: pygame.Surface, entity, screen_pos: Tuple[int, int]) -> bool:
        """Render entity at full quality"""
        screen_x, screen_y = screen_pos
        
        # Multi-part sprites
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
                
                if self._is_on_screen(surface, render_x, render_y, scaled_sprite.get_width(), scaled_sprite.get_height()):
                    surface.blit(scaled_sprite, (render_x, render_y))
            return True
        
        # Single sprite
        if entity.sprite:
            if entity.scale != (1.0, 1.0):
                scaled_w = int(entity.sprite.get_width() * entity.scale[0])
                scaled_h = int(entity.sprite.get_height() * entity.scale[1])
                scaled_sprite = pygame.transform.scale(entity.sprite, (scaled_w, scaled_h))
            else:
                scaled_sprite = entity.sprite
            
            render_x = screen_x - scaled_sprite.get_width() // 2
            render_y = screen_y - scaled_sprite.get_height() // 2
            
            if self._is_on_screen(surface, render_x, render_y, scaled_sprite.get_width(), scaled_sprite.get_height()):
                surface.blit(scaled_sprite, (render_x, render_y))
                return True
        
        return False
    
    def _render_entity_reduced(self, surface: pygame.Surface, entity, entity_idx: int, screen_pos: Tuple[int, int]) -> bool:
        """Render entity at reduced quality"""
        screen_x, screen_y = screen_pos
        sprite = self._get_reduced_sprite(entity, entity_idx)
        
        render_x = screen_x - sprite.get_width() // 2
        render_y = screen_y - sprite.get_height() // 2
        
        if self._is_on_screen(surface, render_x, render_y, sprite.get_width(), sprite.get_height()):
            surface.blit(sprite, (render_x, render_y))
            return True
        return False
    
    def _render_entity_minimal(self, surface: pygame.Surface, entity, entity_idx: int, screen_pos: Tuple[int, int]) -> bool:
        """Render entity at minimal quality (tiny billboard)"""
        screen_x, screen_y = screen_pos
        sprite = self._get_minimal_sprite(entity, entity_idx)
        
        render_x = screen_x - 2  # Center 4x4 sprite
        render_y = screen_y - 2
        
        if self._is_on_screen(surface, render_x, render_y, 4, 4):
            surface.blit(sprite, (render_x, render_y))
            return True
        return False
    
    def _is_on_screen(self, surface: pygame.Surface, x: int, y: int, w: int, h: int) -> bool:
        """Check if rect is visible on screen"""
        return not (x + w < 0 or x > surface.get_width() or y + h < 0 or y > surface.get_height())
    
    def render_optimized(self, surface: pygame.Surface, camera_offset: Tuple[int, int], force_scene_tags: Optional[set] = None, exclude_scene_tags: Optional[set] = None) -> Dict[str, int]:
        """
        Render entities with LOD system.
        
        Returns:
            Dict with stats: {
                'full': count, 
                'reduced': count,
                'minimal': count,
                'culled': count,
                'total_visible': count
            }
        """
        cam_center = (camera_offset[0] + surface.get_width() // 2, camera_offset[1] + surface.get_height() // 2)
        
        # Get nearby entities using spatial grid (wider radius to avoid pop-in)
        nearby_indices = self.spatial_grid.get_nearby_entities(cam_center, radius_cells=6)

        # Always include forced scene entities regardless of distance
        forced_indices = set()
        if force_scene_tags:
            for idx, entity in enumerate(self.entities):
                if not entity.visible:
                    continue
                if exclude_scene_tags and getattr(entity, "scene_tag", None) in exclude_scene_tags:
                    continue
                if getattr(entity, "scene_tag", None) in force_scene_tags:
                    forced_indices.add(idx)
        
        # Always render entities within a near radius at full detail (no budget culling)
        view_w, view_h = surface.get_size()
        near_full_sq = (max(view_w, view_h) * 1.5) ** 2

        # Calculate distances and LOD levels for nearby entities
        render_queue = []
        guaranteed_queue = []
        for idx in nearby_indices:
            if idx >= len(self.entities):
                continue
            
            entity = self.entities[idx]
            if not entity.visible:
                continue
            if exclude_scene_tags and getattr(entity, "scene_tag", None) in exclude_scene_tags:
                continue
            
            # Calculate squared distance (faster than sqrt)
            dx = entity.position[0] - cam_center[0]
            dy = entity.position[1] - cam_center[1]
            dist_sq = dx * dx + dy * dy
            
            if dist_sq <= near_full_sq:
                lod_level = EntityLOD.FULL
            else:
                lod_level = self._get_lod_level(dist_sq)
            
            if lod_level != EntityLOD.CULLED:
                if dist_sq <= near_full_sq:
                    guaranteed_queue.append((dist_sq, lod_level, idx, entity))
                else:
                    render_queue.append((dist_sq, lod_level, idx, entity))
        
        # Sort by distance (render far to near for better occlusion)
        render_queue.sort(key=lambda x: x[0], reverse=True)
        guaranteed_queue.sort(key=lambda x: x[0], reverse=True)
        
        # Apply frame budget (forced entities are rendered separately)
        if len(render_queue) > self.max_per_frame:
            render_queue = render_queue[:self.max_per_frame]
        
        stats = {'full': 0, 'reduced': 0, 'minimal': 0, 'culled': 0, 'total_visible': 0}

        # Build a unified render list so z-index/Y ordering is respected
        draw_items: Dict[int, Tuple[int, object, float]] = {}

        for idx in forced_indices:
            if idx >= len(self.entities):
                continue
            entity = self.entities[idx]
            if not entity.visible:
                continue
            dx = entity.position[0] - cam_center[0]
            dy = entity.position[1] - cam_center[1]
            dist_sq = dx * dx + dy * dy
            draw_items[idx] = (EntityLOD.FULL, entity, dist_sq)

        for dist_sq, lod_level, idx, entity in guaranteed_queue:
            if idx in draw_items:
                continue
            draw_items[idx] = (EntityLOD.FULL, entity, dist_sq)

        for dist_sq, lod_level, idx, entity in render_queue:
            if idx in draw_items:
                continue
            draw_items[idx] = (lod_level, entity, dist_sq)

        draw_list = sorted(
            draw_items.items(),
            key=lambda item: (item[1][1].z_index, item[1][1].position[1], item[1][1].position[0])
        )

        for idx, (lod_level, entity, dist_sq) in draw_list:
            screen_x = entity.position[0] - camera_offset[0]
            screen_y = entity.position[1] - camera_offset[1]
            screen_pos = (screen_x, screen_y)

            rendered = False
            if lod_level == EntityLOD.FULL:
                rendered = self._render_entity_full(surface, entity, screen_pos)
                if rendered:
                    stats['full'] += 1
            elif lod_level == EntityLOD.REDUCED:
                rendered = self._render_entity_reduced(surface, entity, idx, screen_pos)
                if rendered:
                    stats['reduced'] += 1
            elif lod_level == EntityLOD.MINIMAL:
                rendered = self._render_entity_minimal(surface, entity, idx, screen_pos)
                if rendered:
                    stats['minimal'] += 1

            if rendered:
                stats['total_visible'] += 1
        
        # Count culled entities
        stats['culled'] = len(nearby_indices) - stats['total_visible']
        
        # Background processing for far entities (optional, for game logic)
        current_time = time.time()
        if current_time - self.last_background_update > self.background_update_interval:
            self._process_background_entities()
            self.last_background_update = current_time
        
        return stats
    
    def _process_background_entities(self):
        """
        Process off-screen/culled entities at low priority.
        Use this for game logic that should continue even when entities aren't rendered.
        Example: tree growth, berry respawn timers, etc.
        """
        # Placeholder for background processing
        # Add your game logic here that should run even for off-screen entities
        pass
    
    def update_entity_position(self, entity_idx: int, old_pos: Tuple[float, float], new_pos: Tuple[float, float]):
        """Update entity position in spatial grid"""
        if entity_idx < len(self.entities):
            self.spatial_grid.remove_entity(entity_idx, old_pos)
            self.spatial_grid.add_entity(entity_idx, new_pos)
    
    def clear_sprite_caches(self):
        """Clear all sprite caches (call when entities change)"""
        self.reduced_sprite_cache.clear()
        self.minimal_sprite_cache.clear()
    
    def set_lod_distances(self, full: float = 400, reduced: float = 800, minimal: float = 1200):
        """
        Adjust LOD distance thresholds.
        
        Args:
            full: Max distance for full quality rendering
            reduced: Max distance for reduced quality
            minimal: Max distance for minimal quality (beyond this = culled)
        """
        self.lod_distances_sq = {
            EntityLOD.FULL: full ** 2,
            EntityLOD.REDUCED: reduced ** 2,
            EntityLOD.MINIMAL: minimal ** 2,
        }
    
    def set_frame_budget(self, max_entities: int):
        """Set maximum entities to render per frame"""
        self.max_per_frame = max_entities
