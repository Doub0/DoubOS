"""
Croptopia Game Engine - Main Loop
Integrates all TIER 1 systems (signals, scenes, player, tilemap, UI)
"""

import pygame
import sys
from typing import Dict, Optional, Tuple
import os
import re

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

from croptopia.signals import SignalEmitter, EventBus
from croptopia.scene_manager import SceneManager
from croptopia.player import Player
from croptopia.systems.tilemap_renderer import TileMapRenderer
from croptopia.ui.canvas import UICanvas
from croptopia.godot_parser import GodotTSCNParser, SimpleTileMapRenderer
from croptopia.entity_manager import EntityManager
from croptopia.entity_lod_system import EntityLODManager
from croptopia.asset_loader import AssetLoader
from croptopia.npc import NPCManager
from croptopia.dialogue import DialogueSystem, DialogueBox
from croptopia.quest import QuestSystem, QuestUI
from croptopia.zone_transition import ZoneTransitionSystem


class GameEngine:
    """
    Main game engine orchestrating all systems.
    Handles game loop, input processing, rendering pipeline.
    """
    
    # Display settings
    DISPLAY_WIDTH = 1152
    DISPLAY_HEIGHT = 648
    FPS = 60
    
    def __init__(self):
        """Initialize game engine"""
        
        pygame.init()

        # Documentation guardrail: warn if docs not reviewed
        self._check_documentation_status()
        
        # Display setup
        self.display = pygame.display.set_mode((self.DISPLAY_WIDTH, self.DISPLAY_HEIGHT))
        pygame.display.set_caption("Croptopia - Python/Pygame")
        self.clock = pygame.time.Clock()
        self.running = True
        self.delta = 0.0
        
        # Project root (Godot source)
        self.croptopia_root = os.path.join(os.path.dirname(__file__), "..", "Croptopia - 02.11.25")
        self.scene_positions = self._load_worldtest_scene_positions()

        # Load assets (placeholder - TODO: implement asset loader)
        self.assets: Dict = {}  # Will be populated from spritesheet
        self._load_assets()

        # World camera zoom (read from Godot player.tscn)
        self.world_zoom = self._load_player_camera_zoom()
        self.world_surface = None
        
        # Initialize core systems
        print("[Engine] Initializing TIER 1 systems...")
        
        # Load Godot tilemap data with real textures
        print("[Engine] Loading Godot tilemap data with actual textures...")
        godot_path = os.path.join(self.croptopia_root, "scenes", "spawn_node.tscn")
        assets_path = os.path.join(self.croptopia_root, "assets")
        parser = GodotTSCNParser(godot_path, assets_path)
        tilemap_data = parser.parse()
        
        # Scene management (replaces worldtest.gd) - Pass self as engine
        self.scene_manager = SceneManager(self)
        
        # Player system
        spawn_tile = (12, -11)
        tile_size = SimpleTileMapRenderer.TILE_SIZE
        self.player = Player((spawn_tile[0] * tile_size, spawn_tile[1] * tile_size), self.assets)
        
        # Tilemap rendering - use SimpleTileMapRenderer with actual textures
        if tilemap_data:
            self.tilemap = SimpleTileMapRenderer(tilemap_data, assets_path)
        else:
            self.tilemap = TileMapRenderer({}, self.assets)
        
        # Scene tilemaps (loaded on demand when zones are triggered)
        self.scene_tilemaps: Dict[str, Tuple[dict, SimpleTileMapRenderer]] = {}
        self.scene_tilemap_data: Dict[str, dict] = {}
        self.scene_entities_loaded = set()
        
        # Entity management - load all game objects (shrubs, collectables, etc.)
        print("[Engine] Loading game entities...")
        self.entity_manager = EntityManager(godot_path, assets_path)
        self.entity_manager.set_collection_callback(self._on_entity_collected)

        # Entity LOD system - reduces rendering lag
        # LOD enabled with scene-aware visibility
        self.entity_lod = EntityLODManager(self.entity_manager.entities, max_per_frame=400)
        
        # NPC system - create Zea and other NPCs
        print("[Engine] Initializing NPC system...")
        self.npc_manager = NPCManager(self.croptopia_root)
        self.zea = self.npc_manager.create_zea()
        if self.zea:
            print(f"[Engine] Zea created successfully at: {self.zea.position}")
        else:
            print("[Engine] ERROR: Zea creation FAILED")
        
        # Quest state tracking (from worldtest.gd)
        self.quest_is_finished = False
        self.is_pathfollowing = False
        self.cutscene_is_over = False
        
        # Dialogue system
        print("[Engine] Loading dialogue system...")
        self.dialogue_system = DialogueSystem(self.croptopia_root)
        self.dialogue_box = DialogueBox(self.DISPLAY_WIDTH, self.DISPLAY_HEIGHT)
        
        # Quest system
        print("[Engine] Initializing quest system...")
        self.quest_system = QuestSystem(self.croptopia_root)
        self.quest_ui = QuestUI(self.DISPLAY_WIDTH, self.DISPLAY_HEIGHT)
        
        # Connect quest completion signal to NPC quest handler
        self.quest_system.connect_signal("quest_finished", self._on_npc_quest_is_finished)
        
        # Zone transition system
        print("[Engine] Initializing zone transition system...")
        self.zone_system = ZoneTransitionSystem()
        self.zone_system.set_transition_callback(self._on_zone_transition)
        
        # UI canvas
        self.ui = UICanvas((self.DISPLAY_WIDTH, self.DISPLAY_HEIGHT), self.croptopia_root)
        
        # Connect signals
        self._setup_signal_connections()
        
        print("[Engine] TIER 1 systems initialized")
        print("[Engine] Starting main game loop...")
    
    def quit(self):
        """Quit the game (called from menu buttons)"""
        self.running = False
    
    def run(self) -> None:
        """
        Main game loop.
        - Input processing
        - Update all systems
        - Render all systems
        """
        
        while self.running:
            try:
                # Calculate delta time
                self.delta = self.clock.tick(self.FPS) / 1000.0
                
                # Handle input
                self._handle_input()
                
                # Update systems
                self._update_systems()
                
                # Render systems
                self._render_systems()
                
                # Update display
                pygame.display.flip()
            except Exception as e:
                print(f"[Engine] Game loop error: {e}")
                import traceback
                traceback.print_exc()
                self.running = False
    
    def _handle_input(self) -> None:
        """Process keyboard and mouse input"""
        
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                print("[Engine] QUIT event received")
                self.running = False
            
            elif event.type == pygame.KEYDOWN:
                # F10 to toggle collision display
                if event.key == pygame.K_F10:
                    self.debug_show_collision = not self.debug_show_collision
                
                # ESC to quit
                elif event.key == pygame.K_ESCAPE:
                    self.running = False
                
                # E key to interact with NPCs
                elif event.key == pygame.K_e:
                    self._handle_npc_interaction()
                
                # Space/Enter to advance dialogue
                elif event.key in (pygame.K_SPACE, pygame.K_RETURN):
                    if self.dialogue_system.is_active():
                        if not self.dialogue_box.fully_revealed:
                            self.dialogue_box.skip_to_end()
                        elif not self.dialogue_system.next_dialogue_line():
                            # Dialogue finished
                            self.dialogue_system.end_dialogue()
                            self.dialogue_box.hide()
                            # Resume NPC roaming
                            nearby_npc = self.npc_manager.get_nearby_npc(self.player.position)
                            if nearby_npc:
                                nearby_npc.end_chat()
                        else:
                            # Show next line
                            line = self.dialogue_system.get_current_line()
                            if line:
                                self.dialogue_box.show_line(line)
                
                # Number keys (1-8) for hotbar selection
                elif pygame.K_1 <= event.key <= pygame.K_8:
                    slot = event.key - pygame.K_1
                    self.ui.hotbar.select_slot(slot)
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Handle UI clicks
                mouse_pos = pygame.mouse.get_pos()
                self.ui.handle_mouse_click(mouse_pos)
        
        # Continuous key input for movement
        keys = pygame.key.get_pressed()
        mouse_buttons = pygame.mouse.get_pressed()
        self.player.handle_input(keys, mouse_buttons)
    
    def quit(self):
        """Quit the game"""
        print("[Engine] Quit requested")
        self.running = False
    
    def _update_systems(self) -> None:
        """Update all game systems"""
        
        current_scene = self.scene_manager.get_active_scene()
        menu_scenes = ['main_menu', 'settings', 'credits']
        
        # For menu scenes, only update the scene
        if current_scene and current_scene.name in menu_scenes:
            current_scene.update(self.delta)
            return
        
        # For gameplay scenes, update all systems
        # Update player
        self.player.update(self.delta)
        
        # Check for zone transitions (Area2D scene triggers)
        # Zone system will call _on_zone_transition callback automatically
        zone_name = self.zone_system.check_transitions(self.player.position)
        
        # Check for entity collection (player walking near collectables)
        if self.entity_lod:
            nearby_indices = self.entity_lod.get_nearby_entity_indices(
                (self.player.position.x, self.player.position.y),
                radius_cells=1
            )
            self.entity_manager.check_collection_nearby(self.player.position, nearby_indices)
        else:
            self.entity_manager.check_collection(self.player.position)
        
        # Update NPCs
        self.npc_manager.update(self.delta, self.player.position)
        
        # Update dialogue box
        self.dialogue_box.update(self.delta)
        
        # Update tilemap visibility based on camera
        camera_offset = self._get_world_camera_offset()
        viewport_size = self._get_world_viewport_size()
        self.tilemap.update(camera_offset, viewport_size)
        
        # Update UI
        self.ui.update(self.delta)
        
        # Update scene
        if current_scene:
            current_scene.update(self.delta)
    
    def _render_systems(self) -> None:
        """
        Render all systems in order.
        Implements proper layer ordering.
        
        Special handling for menu scenes (main_menu, settings, credits)
        which should NOT render the game world.
        """
        
        current_scene = self.scene_manager.get_active_scene()
        
        # For menu scenes, only render the scene itself
        menu_scenes = ['main_menu', 'settings', 'credits']
        if current_scene and current_scene.name in menu_scenes:
            # Clear and render only the menu scene
            self.display.fill((0, 0, 0))  # Black background
            current_scene.render(self.display)
            return
        
        # For gameplay scenes, render full world
        camera_offset = self._get_world_camera_offset()
        view_w, view_h = self._get_world_viewport_size()

        # If zoomed, render world to offscreen surface and scale to display
        if self.world_zoom.x != 1.0 or self.world_zoom.y != 1.0:
            world_w, world_h = self._get_world_viewport_size()
            if self.world_surface is None or self.world_surface.get_size() != (world_w, world_h):
                self.world_surface = pygame.Surface((world_w, world_h))

            # Clear world surface
            self.world_surface.fill((100, 150, 80))

            # Render game world (tilemap + entities + player)
            self.tilemap.render(self.world_surface, camera_offset)
            
            # Render any loaded scene tilemaps (cull far scenes)
            for scene_name, (tilemap_data, renderer) in self.scene_tilemaps.items():
                if self._should_render_scene_tilemap(tilemap_data, view_w, view_h):
                    renderer.render(self.world_surface, camera_offset)

            if self.entity_lod:
                force_tags = self._get_visible_scene_tags(view_w, view_h)
                if force_tags:
                    count = self.entity_manager.render_scene_tags(self.world_surface, camera_offset, force_tags)
                    print(f"[Engine] Rendered {count} scene entities for tags: {force_tags}")
                self.entity_lod.render_optimized(self.world_surface, camera_offset, force_scene_tags=None, exclude_scene_tags=force_tags)
            else:
                self.entity_manager.render(self.world_surface, camera_offset)
            self.player.render(self.world_surface, camera_offset)

            # Debug rendering (before scaling)
            if self.debug_show_collision:
                self.tilemap.render_collision_overlay(self.world_surface, camera_offset, 80)

            # Scale down to display
            scaled_world = pygame.transform.scale(self.world_surface, (self.DISPLAY_WIDTH, self.DISPLAY_HEIGHT))
            self.display.blit(scaled_world, (0, 0))
        else:
            # Clear display with grass green
            self.display.fill((100, 150, 80))  # Grass green background
            
            # Render game world (tilemap + entities + NPCs + player)
            self.tilemap.render(self.display, camera_offset)
            
            # Render any loaded scene tilemaps (cull far scenes)
            for scene_name, (tilemap_data, renderer) in self.scene_tilemaps.items():
                if self._should_render_scene_tilemap(tilemap_data, view_w, view_h):
                    renderer.render(self.display, camera_offset)

            if self.entity_lod:
                force_tags = self._get_visible_scene_tags(view_w, view_h)
                if force_tags:
                    count = self.entity_manager.render_scene_tags(self.display, camera_offset, force_tags)
                    print(f"[Engine] Rendered {count} scene entities for tags: {force_tags}")
                self.entity_lod.render_optimized(self.display, camera_offset, force_scene_tags=None, exclude_scene_tags=force_tags)
            else:
                self.entity_manager.render(self.display, camera_offset)
            self.npc_manager.render(self.display, camera_offset)
            self.player.render(self.display, camera_offset)
        
        # Render current scene on top (for cutscenes, etc.)
        if current_scene:
            current_scene.render(self.display)
        
        # Render UI canvas last (on top of everything)
        if not (current_scene and current_scene.name in menu_scenes):
            self.ui.render(self.display)
        
        # Render dialogue box on top of UI
        self.dialogue_box.render(self.display)
        
        # Render quest UI
        active_quest = self.quest_system.get_active_quest()
        self.quest_ui.render(self.display, active_quest)
        
        # Debug rendering (non-zoomed path)
        if self.debug_show_collision and self.world_zoom.x == 1.0 and self.world_zoom.y == 1.0:
            self.tilemap.render_collision_overlay(self.display, camera_offset, 80)

    def _get_world_camera_offset(self) -> pygame.Vector2:
        """Get camera offset adjusted for world zoom."""
        if self.world_zoom.x == 1.0 and self.world_zoom.y == 1.0:
            return self.player.camera_offset

        world_w, world_h = self._get_world_viewport_size()
        view_center = pygame.Vector2(world_w / 2, world_h / 2)
        return pygame.Vector2(self.player.position) - view_center

    def _get_world_viewport_size(self) -> Tuple[int, int]:
        """Get world viewport size adjusted for zoom.
        Higher zoom = more zoomed in = smaller world viewport.
        """
        return (
            int(self.DISPLAY_WIDTH / self.world_zoom.x),
            int(self.DISPLAY_HEIGHT / self.world_zoom.y)
        )

    def _should_render_scene_tilemap(self, tilemap_data: dict, view_w: int, view_h: int) -> bool:
        """Cull distant scene tilemaps based on player distance to scene origin."""
        tile_bounds = tilemap_data.get('tile_bounds')
        tilemap_offset = tilemap_data.get('tilemap_offset', (0, 0))

        if tile_bounds:
            min_x, max_x, min_y, max_y = tile_bounds
            tile_size = SimpleTileMapRenderer.TILE_SIZE

            min_px = tilemap_offset[0] + (min_x * tile_size)
            max_px = tilemap_offset[0] + ((max_x + 1) * tile_size)
            min_py = tilemap_offset[1] + (min_y * tile_size)
            max_py = tilemap_offset[1] + ((max_y + 1) * tile_size)

            pad_x = view_w * 2
            pad_y = view_h * 2

            px = self.player.position[0]
            py = self.player.position[1]

            return (min_px - pad_x) <= px <= (max_px + pad_x) and (min_py - pad_y) <= py <= (max_py + pad_y)

        scene_origin = tilemap_data.get('scene_origin')
        if not scene_origin:
            return True

        dx = self.player.position[0] - scene_origin[0]
        dy = self.player.position[1] - scene_origin[1]

        # Render only if within a generous range of the viewport
        return abs(dx) <= view_w * 2 and abs(dy) <= view_h * 2

    def _get_visible_scene_tags(self, view_w: int, view_h: int) -> set:
        """Get scene tags that should be forced visible in LOD rendering."""
        visible_tags = set()
        for scene_name, (tilemap_data, _) in self.scene_tilemaps.items():
            if self._should_render_scene_tilemap(tilemap_data, view_w, view_h):
                visible_tags.add(scene_name)
        if visible_tags:
            print(f"[Engine] Visible scene tags for entity rendering: {visible_tags}")
        return visible_tags

    def _load_player_camera_zoom(self) -> pygame.Vector2:
        """Read Camera2D zoom from Godot player.tscn."""
        try:
            player_tscn = os.path.join(self.croptopia_root, "scenes", "player.tscn")
            if not os.path.exists(player_tscn):
                return pygame.Vector2(1.0, 1.0)

            with open(player_tscn, "r", encoding="utf-8") as f:
                content = f.read()

            match = re.search(r'zoom = Vector2\(([-\d.]+),\s*([-\d.]+)\)', content)
            if not match:
                return pygame.Vector2(1.0, 1.0)

            return pygame.Vector2(float(match.group(1)), float(match.group(2)))
        except Exception:
            return pygame.Vector2(1.0, 1.0)

    def _load_worldtest_scene_positions(self) -> Dict[str, Tuple[float, float]]:
        """Read scene marker positions from worldtest.tscn to place scenes correctly."""
        positions: Dict[str, Tuple[float, float]] = {}
        try:
            # 1) Use marker positions in worldtest.tscn (scene spawn points)
            worldtest_tscn = os.path.join(self.croptopia_root, "scenes", "worldtest.tscn")
            if not os.path.exists(worldtest_tscn):
                return positions

            with open(worldtest_tscn, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            def get_marker_pos(marker_name: str) -> Tuple[float, float]:
                pattern = rf'\[node name="{re.escape(marker_name)}"[^\]]*\](.*?)(?=\n\[node|\Z)'
                match = re.search(pattern, content, re.DOTALL)
                if not match:
                    return None
                block = match.group(1)
                pos_match = re.search(r'position = Vector2\(([-\d.]+),\s*([-\d.]+)\)', block)
                if not pos_match:
                    return None
                return (float(pos_match.group(1)), float(pos_match.group(2)))

            # Worldtest marker nodes that define scene placement
            positions_map = {
                "shelburne_road": "shelburne_road_pos",
                "shelburne": "shelburne_pos",
                "michael_plot": "michael_plot_pos",
            }

            for scene_name, marker_name in positions_map.items():
                pos = get_marker_pos(marker_name)
                if pos:
                    positions[scene_name] = pos

            # 2) Fallback to worldtest.gd instance positions if marker missing
            worldtest_gd = os.path.join(self.croptopia_root, "scenes", "worldtest.gd")
            if os.path.exists(worldtest_gd):
                with open(worldtest_gd, 'r', encoding='utf-8', errors='ignore') as f:
                    gd_content = f.read()

                def get_gd_position(scene_var: str) -> Optional[Tuple[float, float]]:
                    pattern = rf'{re.escape(scene_var)}\.position\s*=\s*Vector2\(([-\d.]+),\s*([-\d.]+)\)'
                    match = re.search(pattern, gd_content)
                    if not match:
                        return None
                    return (float(match.group(1)), float(match.group(2)))

                gd_map = {
                    "shelburne_road": "shelburne_road_instance",
                    "shelburne": "shelburne_instance",
                    "michael_plot": "michael_plot_instance",
                }

                for scene_name, var_name in gd_map.items():
                    if scene_name in positions:
                        continue
                    pos = get_gd_position(var_name)
                    if pos:
                        positions[scene_name] = pos

            return positions
        except Exception as e:
            print(f"[Engine] Error loading worldtest scene positions: {e}")
            return positions
    
    def _setup_signal_connections(self) -> None:
        """
        Connect signals between systems.
        Implements signal routing that was in worldtest.gd.
        """
        
        # Player signals
        self.player.on_signal('item_holding', self._on_player_item_holding)
        self.player.on_signal('stick_collected', self._on_stick_collected)
        self.player.on_signal('redbane_selected', self._on_redbane_selected)
        
        # Scene manager signals
        self.scene_manager.on_signal('scene_changed', self._on_scene_changed)
        
        # UI signals
        self.ui.on_signal('dialog_shown', self._on_dialog_shown)
        self.ui.on_signal('dialog_hidden', self._on_dialog_hidden)
        
        print("[Engine] Signal connections established")
    
    def _on_player_item_holding(self, item_type: str) -> None:
        """Handle player selecting item"""
        print(f"[Engine] Player holding: {item_type}")
    
    def _on_stick_collected(self) -> None:
        """Handle stick collection"""
        self.ui.hud.set_money(self.ui.hud.money + 10)
        print("[Engine] Stick collected! +10 money")
        
        # Add to quest tracking
        self.quest_system.add_item("stick", 1)
    
    def _on_redbane_selected(self) -> None:
        """Handle redbaneberry selection"""
        print("[Engine] Redbaneberry selected")
    
    def _handle_npc_interaction(self) -> None:
        """Handle E key pressed for NPC interaction."""
        # Check if dialogue already active
        if self.dialogue_system.is_active():
            return
        
        # Find nearby NPC
        nearby_npc = self.npc_manager.get_nearby_npc(self.player.position, radius=50.0)
        if nearby_npc:
            # Start dialogue
            nearby_npc.start_chat()
            dialogue_file = nearby_npc.get_dialogue_file()
            
            if self.dialogue_system.start_dialogue(dialogue_file):
                # Show first line
                line = self.dialogue_system.get_current_line()
                if line:
                    self.dialogue_box.show_line(line)
                    
                    # If this is Zea's first dialogue, start the quest
                    if nearby_npc.name == "Zea" and dialogue_file == "dialouge/zea_dialogue.json":
                        self.quest_system.start_quest("zea_medicine")
                        print("[Engine] Zea's quest started!")
            else:
                # Dialogue file not found
                nearby_npc.end_chat()
    
    def _handle_entity_collected(self, entity_type: str):
        """Handle entity collection (shrubs, pinecones, etc.)."""
        # Map entity types to quest item names
        item_mapping = {
            "shrub_pinecone": "pinecone",
            "pinecone": "pinecone",
            "stick": "stick",
            "sorrel": "sorrel",
            "redbaneberry": "redbaneberry",
            "chives": "chives",
            "elderberry": "elderberry",
        }
        
        item_name = item_mapping.get(entity_type)
        if item_name:
            self.quest_system.add_item(item_name, 1)
    
    def _on_entity_collected(self, item_type: str):
        """Callback when entity is collected by entity manager."""
        print(f"[Engine] Entity collected: {item_type}")
        self.quest_system.add_item(item_type, 1)
        
        # Also give money for sticks (legacy behavior)
        if item_type == "stick":
            self.ui.hud.set_money(self.ui.hud.money + 10)
    
    def _on_npc_quest_is_finished(self):
        """
        Callback from NPC when quest is complete.
        From worldtest.gd: _on_npc_quest_is_finished()
        """
        print("[Engine] QUEST COMPLETE - Starting Zea walk cutscene...")
        self.quest_is_finished = True
        
        # Move player to cutscene start position
        self.player.position = (-1000, 0)
        self.is_pathfollowing = True
        
        # Start the Zea walk cutscene
        self.zea_walk_cutscene()
    
    def zea_walk_cutscene(self):
        """
        Execute Zea walk cutscene after quest completion.
        From worldtest.gd: zea_walk_cutscene()
        
        Loads zea_walk_cutscene.tscn and plays animation sequence.
        """
        print("[Engine] Loading Zea walk cutscene...")
        
        # TODO: Load zea_walk_cutscene.tscn from Godot
        # Position at (-297, -1287)
        # Connect "cutscene_over" signal to second_zea_cutscene()
        # Disable player camera
        
        # For now, just move to second cutscene
        self.second_zea_cutscene()
    
    def second_zea_cutscene(self):
        """
        Execute second cutscene (scenetwo.tscn).
        From worldtest.gd: second_zea_cutscene()
        """
        print("[Engine] Loading second Zea cutscene...")
        
        # TODO: Load scenetwo.tscn from Godot
        # Position at (-5091.517, -3156.3)
        # Connect "cutscene_finished" signal to second_zea_over()
        
        # For now, just finish
        self.second_zea_over()
    
    def second_zea_over(self):
        """
        Second cutscene finished callback.
        From worldtest.gd: second_zea_over()
        """
        print("[Engine] Second cutscene finished - Moving to Shelburne...")
        self.cutscene_is_over = True
        
        # Generate Shelburne scene
        self.generate_shelburne()
    
    def _on_zone_transition(self, zone_name: str):
        """
        Handle zone transition triggered by Area2D.
        Based on worldtest.gd scene generation logic.
        """
        print(f"\n[Engine] *** ZONE TRANSITION TRIGGERED: {zone_name} ***\n")
        
        # Handle specific zone transitions
        if zone_name == "shelburne_road":
            # From worldtest.gd: generate_shelburne_road()
            # Position: Vector2(-3200,-2949)
            print("[Engine] -> Generating Shelburne Road...")
            self.generate_shelburne_road()
            
        elif zone_name == "shelburne":
            # From worldtest.gd: generate_shelburne()
            # Position: Vector2(-10388,-1849)
            print("[Engine] -> Generating Shelburne town...")
            self.generate_shelburne()
            
        elif zone_name == "michael_plot":
            # From worldtest.gd: generate_michael_plot()
            # Position: Vector2(-2845,-2985)
            print("[Engine] -> Generating Michael's Plot...")
            self.generate_michael_plot()
            
        elif zone_name == "mount_crag":
            # From shelburne.gd: top_of_mt_crag
            print("[Engine] -> Entering Mount Crag...")
            # TODO: Load mount_crag scene
    
    def generate_shelburne_road(self):
        """
        Generate Shelburne Road scene.
        From worldtest.gd: generate_shelburne_road()
        
        Loads testing.tscn at position (-3200, -2949) and creates Zea.
        """
        print("[Engine] Generating Shelburne Road at (-3200, -2949)...")
        
        # Load tilemap if not already cached
        if "shelburne_road" not in self.scene_tilemap_data:
            try:
                testing_path = os.path.join(self.croptopia_root, "testing.tscn")
                assets_path = os.path.join(self.croptopia_root, "assets")
                parser = GodotTSCNParser(testing_path, assets_path)
                tilemap_data = parser.parse()
                
                if tilemap_data:
                    scene_offset = self.scene_positions.get("shelburne_road", (-3200.0, -2949.0))
                    tilemap_data['tilemap_offset'] = (
                        tilemap_data.get('tilemap_offset', (0, 0))[0] + scene_offset[0],
                        tilemap_data.get('tilemap_offset', (0, 0))[1] + scene_offset[1],
                    )
                    tilemap_data['scene_origin'] = scene_offset
                    renderer = SimpleTileMapRenderer(tilemap_data, assets_path)
                    renderer.map_offset = tilemap_data['tilemap_offset']
                    self.scene_tilemaps["shelburne_road"] = (tilemap_data, renderer)
                    self.scene_tilemap_data["shelburne_road"] = tilemap_data
                    print("[Engine] Shelburne Road tilemap loaded")
            except Exception as e:
                print(f"[Engine] Error loading shelburne_road: {e}")

        # Load ALL scene entities (every single child instance) with world offset
        if "shelburne_road" not in self.scene_entities_loaded:
            try:
                testing_path = os.path.join(self.croptopia_root, "testing.tscn")
                scene_offset = self.scene_positions.get("shelburne_road", (-3200.0, -2949.0))
                added = self.entity_manager.add_scene_entities(testing_path, scene_offset=scene_offset, scene_tag="shelburne_road")
                self.scene_entities_loaded.add("shelburne_road")
                if self.entity_lod:
                    self.entity_lod.rebuild_spatial_grid()
                print(f"[Engine] Shelburne Road entities added: {added}")
            except Exception as e:
                print(f"[Engine] Error loading shelburne_road entities: {e}")
        
        # Generate Zea if not already created
        if not self.zea:
            self.generate_zea()
    
    def generate_zea(self):
        """
        Generate Zea NPC at spawn location.
        From worldtest.gd: generate_zea()
        """
        print("[Engine] Generating Zea at (-297, -1287)...")
        
        # Zea already created in __init__, just need to connect quest signal
        if self.zea:
            # Connect quest completion signal
            if hasattr(self.zea, 'connect_signal'):
                self.zea.connect_signal("quest_is_finished", self._on_npc_quest_is_finished)
            
            # Set Z-index for proper layering
            self.zea.z_index = 2
    
    def generate_shelburne(self):
        """
        Generate Shelburne scene.
        From worldtest.gd: generate_shelburne()
        
        Loads shelburne.tscn at position (-10388, -1849).
        """
        print("[Engine] Generating Shelburne at (-10388, -1849)...")
        
        # Load tilemap if not already cached
        if "shelburne" not in self.scene_tilemap_data:
            try:
                shelburne_path = os.path.join(self.croptopia_root, "shelburne.tscn")
                assets_path = os.path.join(self.croptopia_root, "assets")
                parser = GodotTSCNParser(shelburne_path, assets_path)
                tilemap_data = parser.parse()
                
                if tilemap_data:
                    scene_offset = self.scene_positions.get("shelburne", (-10388.0, -1849.0))
                    tilemap_data['tilemap_offset'] = (
                        tilemap_data.get('tilemap_offset', (0, 0))[0] + scene_offset[0],
                        tilemap_data.get('tilemap_offset', (0, 0))[1] + scene_offset[1],
                    )
                    tilemap_data['scene_origin'] = scene_offset
                    renderer = SimpleTileMapRenderer(tilemap_data, assets_path)
                    renderer.map_offset = tilemap_data['tilemap_offset']
                    self.scene_tilemaps["shelburne"] = (tilemap_data, renderer)
                    self.scene_tilemap_data["shelburne"] = tilemap_data
                    print("[Engine] Shelburne tilemap loaded")
            except Exception as e:
                print(f"[Engine] Error loading shelburne: {e}")

        # Load ALL scene entities (every single child instance) with world offset
        if "shelburne" not in self.scene_entities_loaded:
            try:
                shelburne_path = os.path.join(self.croptopia_root, "shelburne.tscn")
                scene_offset = self.scene_positions.get("shelburne", (-10388.0, -1849.0))
                added = self.entity_manager.add_scene_entities(shelburne_path, scene_offset=scene_offset, scene_tag="shelburne")
                self.scene_entities_loaded.add("shelburne")
                if self.entity_lod:
                    self.entity_lod.rebuild_spatial_grid()
                print(f"[Engine] Shelburne entities added: {added}")
            except Exception as e:
                print(f"[Engine] Error loading shelburne entities: {e}")
    
    def generate_michael_plot(self):
        """
        Generate Michael Plot scene.
        From worldtest.gd: generate_michael_plot()
        
        Loads michael_plot.tscn at position (-2845, -2985).
        """
        print("[Engine] Generating Michael Plot at (-2845, -2985)...")
        
        # Load tilemap if not already cached
        if "michael_plot" not in self.scene_tilemap_data:
            try:
                michael_plot_path = os.path.join(self.croptopia_root, "scenes", "michael_plot.tscn")
                assets_path = os.path.join(self.croptopia_root, "assets")
                parser = GodotTSCNParser(michael_plot_path, assets_path)
                tilemap_data = parser.parse()
                
                if tilemap_data:
                    scene_offset = self.scene_positions.get("michael_plot", (-2845.0, -2985.0))
                    tilemap_data['tilemap_offset'] = (
                        tilemap_data.get('tilemap_offset', (0, 0))[0] + scene_offset[0],
                        tilemap_data.get('tilemap_offset', (0, 0))[1] + scene_offset[1],
                    )
                    tilemap_data['scene_origin'] = scene_offset
                    renderer = SimpleTileMapRenderer(tilemap_data, assets_path)
                    renderer.map_offset = tilemap_data['tilemap_offset']
                    self.scene_tilemaps["michael_plot"] = (tilemap_data, renderer)
                    self.scene_tilemap_data["michael_plot"] = tilemap_data
                    print("[Engine] Michael Plot tilemap loaded")
            except Exception as e:
                print(f"[Engine] Error loading michael_plot: {e}")

        # Load ALL scene entities (every single child instance) with world offset
        if "michael_plot" not in self.scene_entities_loaded:
            try:
                michael_plot_path = os.path.join(self.croptopia_root, "scenes", "michael_plot.tscn")
                scene_offset = self.scene_positions.get("michael_plot", (-2845.0, -2985.0))
                added = self.entity_manager.add_scene_entities(michael_plot_path, scene_offset=scene_offset, scene_tag="michael_plot")
                self.scene_entities_loaded.add("michael_plot")
                if self.entity_lod:
                    self.entity_lod.rebuild_spatial_grid()
                print(f"[Engine] Michael Plot entities added: {added}")
            except Exception as e:
                print(f"[Engine] Error loading michael_plot entities: {e}")
    
    def mt_crag_cutscene_over(self):
        """
        Mount Crag cutscene finished callback.
        From worldtest.gd: mt_crag_cutscene_over()
        """
        print("[Engine] Mount Crag cutscene finished")
        
        # Move player to Michael Plot
        self.player.position = (-2845, -2985)
    
    def _on_scene_changed(self, scene_name: str) -> None:
        """Handle scene transition"""
        print(f"[Engine] Transitioned to scene: {scene_name}")
    
    def _on_dialog_shown(self, character: str, text: str) -> None:
        """Handle dialog appearance"""
        print(f"[Engine] Dialog shown: {character}")
    
    def _on_dialog_hidden(self) -> None:
        """Handle dialog disappearance"""
        print("[Engine] Dialog hidden")
    
    def _load_assets(self) -> None:
        """
        Load sprite assets.
        TODO: Implement spritesheet loading from croptopia_assets/
        
        For now, assets are placeholders that will be replaced with:
        - player sprites (8 directions × 2 movement types × 4 frames each)
        - tile sprites (220+ tiles for 6 layers)
        - UI sprites (hotbar, buttons, portraits)
        - NPC sprites (Zea dialogue frames, movement frames)
        """
        
        print("[Engine] Loading assets...")
        self.assets.update(AssetLoader.load_player_assets(self.croptopia_root))

    def _check_documentation_status(self) -> None:
        """Warn if documentation checklist still has pending items."""

        try:
            repo_root = os.path.join(os.path.dirname(__file__), "..")
            index_path = os.path.join(repo_root, "CROPTOPIA_MD_INDEX.md")
            if not os.path.exists(index_path):
                return
            with open(index_path, "r", encoding="utf-8", errors="ignore") as f:
                lines = f.readlines()
            pending = [line.strip() for line in lines if line.strip().startswith("- [ ]")]
            if pending:
                print("[Docs] WARNING: Documentation checklist has pending items:")
                for item in pending[:15]:
                    print(f"  {item}")
                if len(pending) > 15:
                    print(f"  ... and {len(pending) - 15} more")
        except Exception as e:
            print(f"[Docs] WARNING: Unable to read documentation index: {e}")
    
    def shutdown(self) -> None:
        """Clean shutdown"""
        print("[Engine] Shutting down...")
        pygame.quit()
        print("[Engine] Bye!")
    
    # Debug settings
    debug_show_collision = False


def main():
    """Entry point"""
    
    print("=" * 60)
    print("CROPTOPIA - Python/Pygame Implementation")
    print("TIER 1: Foundation Systems")
    print("=" * 60)
    print()
    
    engine = GameEngine()
    
    try:
        engine.run()
    except KeyboardInterrupt:
        print("\n[Engine] Interrupted by user")
    finally:
        engine.shutdown()


if __name__ == "__main__":
    main()
