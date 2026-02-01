"""
Croptopia Game Engine - Main Loop
Integrates all TIER 1 systems (signals, scenes, player, tilemap, UI)
"""

import pygame
import sys
from typing import Dict, Optional
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

from croptopia.signals import SignalEmitter, EventBus
from croptopia.scene_manager import SceneManager
from croptopia.player import Player
from croptopia.systems.tilemap_renderer import TileMapRenderer
from croptopia.ui.canvas import UICanvas
from croptopia.godot_parser import GodotTSCNParser, SimpleTileMapRenderer
from croptopia.entity_manager import EntityManager
from croptopia.asset_loader import AssetLoader


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

        # Load assets (placeholder - TODO: implement asset loader)
        self.assets: Dict = {}  # Will be populated from spritesheet
        self._load_assets()
        
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
        
        # Entity management - load all game objects (shrubs, collectables, etc.)
        print("[Engine] Loading game entities...")
        self.entity_manager = EntityManager(godot_path, assets_path)
        
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
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Handle UI clicks
                mouse_pos = pygame.mouse.get_pos()
                self.ui.handle_mouse_click(mouse_pos)
    
    def quit(self):
        """Quit the game"""
        print("[Engine] Quit requested")
        self.running = False
        
        # Continuous key input for movement
        keys = pygame.key.get_pressed()
        mouse_buttons = pygame.mouse.get_pressed()
        self.player.handle_input(keys, mouse_buttons)
    
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
        
        # Update tilemap visibility based on camera
        self.tilemap.update(self.player.camera_offset, 
                          (self.DISPLAY_WIDTH, self.DISPLAY_HEIGHT))
        
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
        # Clear display with grass green
        self.display.fill((100, 150, 80))  # Grass green background
        
        # Render game world (tilemap + entities + player)
        self.tilemap.render(self.display, self.player.camera_offset)
        
        # Render entities (shrubs, collectables, etc.) - between tilemap and player
        self.entity_manager.render(self.display, self.player.camera_offset)
        
        # Render player on top
        self.player.render(self.display, self.player.camera_offset)
        
        # Render current scene on top (for cutscenes, etc.)
        if current_scene:
            current_scene.render(self.display)
        
        # Render UI canvas last (on top of everything) - but NOT on menu scenes
        if not (current_scene and current_scene.name in menu_scenes):
            self.ui.render(self.display)
        
        # Debug rendering
        if self.debug_show_collision:
            self.tilemap.render_collision_overlay(self.display, self.player.camera_offset, 80)
    
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
    
    def _on_redbane_selected(self) -> None:
        """Handle redbaneberry selection"""
        print("[Engine] Redbaneberry selected")
    
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
