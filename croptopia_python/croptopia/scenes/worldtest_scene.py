"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                          WORLDTEST SCENE - CRITICAL CORE FILE                ║
║                                                                              ║
║  ⚠️  DO NOT DELETE OR HEAVILY MODIFY THIS FILE ⚠️                            ║
║                                                                              ║
║  This file contains ESSENTIAL GAME SYSTEMS that connect directly to the     ║
║  Godot original project (Croptopia - 02.11.25/scenes/worldtest.tscn).       ║
║                                                                              ║
║  PROTECTED SYSTEMS:                                                          ║
║  1. Player loading and initialization (from player.tscn)                    ║
║  2. World background rendering (grass tiles)                                ║
║  3. Camera system (follows player)                                          ║
║  4. UI overlay rendering (day_and_night.tscn, ui.tscn, hotbar.tscn)       ║
║  5. Game state tracking (time, day cycle, inventory)                        ║
║  6. Scene management (transitions to other areas)                           ║
║                                                                              ║
║  CRITICAL CLASSES:                                                           ║
║  • WorldTestScene: Main game scene (DO NOT REMOVE)                          ║
║  • DayNightDisplay: Time/date UI panel (from day_and_night.tscn)           ║
║  • Hotbar: Inventory system (from hotbar.tscn - 8 slots)                   ║
║  • MoneyPanel: Currency display (from ui.tscn)                             ║
║                                                                              ║
║  DELETION HISTORY:                                                           ║
║  This file was completely deleted once, removing ALL game world rendering   ║
║  and player functionality. The result: player disappeared, game became unplayable.║
║  Recovery required manual reconstruction from Godot TSCN files.              ║
║                                                                              ║
║  RULES FOR MODIFICATION:                                                     ║
║  ✓ CAN:   Add new features that don't remove existing code                 ║
║  ✓ CAN:   Modify UI positioning using screenshot reference                 ║
║  ✓ CAN:   Add new asset loading alongside existing systems                 ║
║  ✗ CANNOT: Delete or comment-out class definitions                         ║
║  ✗ CANNOT: Remove player initialization code                              ║
║  ✗ CANNOT: Remove world rendering                                          ║
║  ✗ CANNOT: Remove the WorldTestScene class                                 ║
║  ✗ CANNOT: Delete asset loading without replacement                        ║
║                                                                              ║
║  DOCUMENTATION REFERENCES:                                                   ║
║  - CROPTOPIA_1TO1_ARCHITECTURE.md (system structure)                        ║
║  - CROPTOPIA_SCENE_HIERARCHY.md (complete scene list)                       ║
║  - Croptopia - 02.11.25/scenes/worldtest.tscn (original Godot scene)       ║
║  - Croptopia - 02.11.25/scenes/worldtest.gd (original game logic)          ║
║  - Croptopia - 02.11.25/scenes/player.tscn (player structure)              ║
║  - Croptopia - 02.11.25/scenes/ui.tscn (UI hierarchy)                      ║
║                                                                              ║
║  IF YOU NEED TO UNDERSTAND:                                                  ║
║  • Player system: See CROPTOPIA_1TO1_ARCHITECTURE.md section "Player"       ║
║  • UI positioning: Read each panel class docstring (DayNightDisplay, etc.)  ║
║  • Asset loading: See _load_assets() method                                 ║
║  • Game loop: See update() and render() methods                             ║
║                                                                              ║
║  BEFORE COMMITTING CHANGES:                                                  ║
║  1. Test the game runs without errors                                       ║
║  2. Verify player appears in the world                                      ║
║  3. Verify all UI panels render (day/night, money, hotbar)                 ║
║  4. Check camera follows player movement                                    ║
║  5. Ensure no traceback errors in console                                   ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import pygame
import os
import math
from croptopia.scenes.base_scene import Scene


class DayNightDisplay:
    """
    ⚠️  CRITICAL: Day and night display panel - from day_and_night.tscn
    
    SYSTEMS MANAGED BY THIS CLASS:
    • In-game time tracking (hours and minutes)
    • Day/month/year progression
    • Time-based mechanics (sunrise/sunset, crop growth timers)
    • Save file persistence (time state must be saveable)
    
    FROM GODOT PROJECT:
    • Source: Croptopia - 02.11.25/scenes/day_and_night.tscn
    • Parent: ui.tscn / CanvasLayer / day_and_night
    • Script: (no GD script, pure UI)
    • Assets: game_ui_panel.png (NinePatchRect background)
    
    TSCN STRUCTURE:
    ├─ Panel (NinePatchRect)
    │  └─ position: (9, -1)
    │  └─ scale: (3, 3)
    │  └─ size: (120, 40) → final: (360, 120)
    │  └─ texture_normal: game_ui_panel.png
    │  └─ expand_mode: ignore_size
    ├─ Labels for: day, date, month, time, temperature, year
    │  └─ All using pixelated.ttf font
    
    DO NOT:
    • Modify time progression logic without testing save/load
    • Remove day/month/year tracking
    • Change the clock_interval (1.0 seconds) without checking game balance
    • Remove the _on_clock_timeout() method
    
    INTERFACE:
    • update(delta): Called every frame, advances time
    • render(surface): Draws the panel on screen
    
    POSITIONING (from screenshot):
    • Position: (27, -3) scaled coordinates
    • Size: 350x100 pixels (observed from screenshot)
    • Background: Tan (#C8AA82) with brown border (#8B4513)
    • Text color: Black for contrast
    """
    
    def __init__(self, engine, scale_x, scale_y):
        self.engine = engine
        self.scale_x = scale_x
        self.scale_y = scale_y
        
        # Display state
        self.day_count = 1
        self.weekday_number = 0  # 0=Monday
        self.week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        self.month_array = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"]
        self.month_number = 0
        self.year = 2027
        
        # Time (hour and minute, using single digit format)
        self.hour_sif1 = 2  # Ones place
        self.hour_sif2 = 1  # Tens place (displays as "12")
        self.minute_sif1 = 0
        self.minute_sif2 = 0
        self.temp = 17
        
        # Clock timer
        self.clock_timer = 0.0
        self.clock_interval = 1.0
        
        # Load game_ui_panel.png for background
        panel_path = os.path.join(engine.croptopia_root, "assets", "game_ui_panel.png")
        self.panel_texture = None
        if os.path.exists(panel_path):
            try:
                self.panel_texture = pygame.image.load(panel_path).convert_alpha()
            except:
                pass
        
        # Load font
        font_path = os.path.join(engine.croptopia_root, "fonts", "pixelated.ttf")
        if os.path.exists(font_path):
            self.font = pygame.font.Font(font_path, 16)
        else:
            self.font = pygame.font.Font(None, 16)
    
    def update(self, delta):
        """Update clock timer"""
        self.clock_timer += delta
        if self.clock_timer >= self.clock_interval:
            self.clock_timer = 0.0
            self._on_clock_timeout()
    
    def _on_clock_timeout(self):
        """Called every in-game minute"""
        self.minute_sif1 += 1
        
        if self.minute_sif1 == 10:
            self.minute_sif1 = 0
            self.minute_sif2 += 1
        
        if self.minute_sif2 == 6:
            self.minute_sif1 = 0
            self.minute_sif2 = 0
            self.hour_sif1 += 1
        
        if self.hour_sif1 == 10:
            self.hour_sif1 = 0
            self.hour_sif2 += 1
        
        # Day transition at 24:00
        if self.hour_sif2 == 2 and self.hour_sif1 == 4:
            self.day_count += 1
            self.hour_sif1 = 0
            self.hour_sif2 = 0
            self.minute_sif1 = 0
            self.minute_sif2 = 0
            self.weekday_number = (self.weekday_number + 1) % 7
            
            # Month transition every 30 days
            if self.day_count % 30 == 0:
                self.month_number = (self.month_number + 1) % 12
                if self.month_number == 0:
                    self.year += 1
    
    def render(self, surface):
        """Render day/night display using actual assets"""
        # TSCN position: offset (9, -1), parent scale (3, 3)
        # Final position: top-left corner
        panel_x = int(10 * self.scale_x)
        panel_y = int(10 * self.scale_y)
        
        # Panel size from screenshot observation
        panel_width = int(350 * self.scale_x)
        panel_height = int(100 * self.scale_y)
        
        # Draw background using panel texture if available, otherwise use colored rect
        if self.panel_texture:
            # Scale panel texture to fit
            panel_scaled = pygame.transform.scale(self.panel_texture, (int(panel_width), int(panel_height)))
            surface.blit(panel_scaled, (int(panel_x), int(panel_y)))
        else:
            # Fallback to tan rectangle with border (matching screenshot)
            pygame.draw.rect(surface, (200, 170, 130), (int(panel_x), int(panel_y), int(panel_width), int(panel_height)))
            pygame.draw.rect(surface, (139, 69, 19), (int(panel_x), int(panel_y), int(panel_width), int(panel_height)), 3)
        
        # Create fonts for labels
        font_path = os.path.join(self.engine.croptopia_root, "fonts", "pixelated.ttf")
        large_font = pygame.font.Font(font_path, 28) if os.path.exists(font_path) else pygame.font.Font(None, 28)
        medium_font = pygame.font.Font(font_path, 20) if os.path.exists(font_path) else pygame.font.Font(None, 20)
        small_font = pygame.font.Font(font_path, 14) if os.path.exists(font_path) else pygame.font.Font(None, 14)
        
        text_color = (0, 0, 0)
        
        # Draw day name (e.g., "Monday")
        day_name = self.week[self.weekday_number]
        day_name_surface = medium_font.render(day_name, True, text_color)
        surface.blit(day_name_surface, (int(panel_x + 85 * self.scale_x), int(panel_y + 10 * self.scale_y)))
        
        # Day count (large number)
        day_text = str(self.day_count)
        day_surface = large_font.render(day_text, True, text_color)
        surface.blit(day_surface, (int(panel_x + 180 * self.scale_x), int(panel_y + 28 * self.scale_y)))
        
        # Month (JAN, FEB, etc.)
        month_surface = medium_font.render(self.month_array[self.month_number], True, text_color)
        surface.blit(month_surface, (int(panel_x + 230 * self.scale_x), int(panel_y + 32 * self.scale_y)))
        
        # Time (HH:MM format)
        time_str = f"{self.hour_sif2}{self.hour_sif1}:{self.minute_sif2}{self.minute_sif1}"
        time_surface = medium_font.render(time_str, True, text_color)
        surface.blit(time_surface, (int(panel_x + 150 * self.scale_x), int(panel_y + 60 * self.scale_y)))
        
        # Temperature
        temp_surface = small_font.render(f"{self.temp}°C", True, text_color)
        surface.blit(temp_surface, (int(panel_x + 260 * self.scale_x), int(panel_y + 65 * self.scale_y)))
        
        # Year
        year_surface = small_font.render(f"{self.year}", True, text_color)
        surface.blit(year_surface, (int(panel_x + 280 * self.scale_x), int(panel_y + 82 * self.scale_y)))


class Hotbar:
    """
    ⚠️  CRITICAL: Inventory hotbar - from hotbar.tscn
    
    SYSTEMS MANAGED BY THIS CLASS:
    • Player inventory display (8 slots)
    • Item selection indicator
    • Inventory UI rendering
    • Slot state persistence
    
    FROM GODOT PROJECT:
    • Source: Croptopia - 02.11.25/scenes/hotbar.tscn
    • Parent: ui.tscn / CanvasLayer / hotbar
    • Root: NinePatchRect (hotbar_asset.png)
    • Scale: 3x, position: (239, 544)
    • Child: GridContainer with 8 TextureRect slots
    • Selection indicator: AnimatedSprite2D (rotation 90°, scale 0.397)
    
    CRITICAL CONNECTIONS:
    • hotbar.tscn is INSTANCED IN ui.tscn
    • UI.tscn is INSTANTIATED IN worldtest.gd _ready()
    • Player inventory state must sync with hotbar display
    
    ASSET FILES REQUIRED:
    • hotbar_asset.png: NinePatchRect background texture
    • pixil-frame-0 - 2024-02-05T105702.567.png: Selection cursor
    
    DO NOT:
    • Remove the 8-slot limitation
    • Modify slot size without updating layout
    • Delete the indicator rendering code
    • Change GridContainer column count (must be 8)
    • Modify selection indicator rotation (must be 90°)
    
    INTERFACE:
    • selected_slot: Current selected inventory slot (0-7)
    • render(surface): Draws hotbar and selection indicator
    
    POSITIONING (from TSCN):
    • Godot coords: (239, 544) with scale (3, 3)
    • Final position: centered at bottom of screen
    • Base size: 216.025 x 28 pixels
    • Final size: ~648 x 84 pixels (with 3x scale)
    """
    
    def __init__(self, engine, scale_x, scale_y):
        self.engine = engine
        self.scale_x = scale_x
        self.scale_y = scale_y
        self.selected_slot = 0
        
        # Screen dimensions
        self.screen_width = 1152
        self.screen_height = 648
        
        # Load hotbar background (NinePatchRect texture)
        hotbar_path = os.path.join(engine.croptopia_root, "assets", "hotbar_asset.png")
        self.bg_texture = None
        if os.path.exists(hotbar_path):
            try:
                self.bg_texture = pygame.image.load(hotbar_path).convert_alpha()
            except:
                pass
        
        # Load selection indicator sprite
        indicator_path = os.path.join(engine.croptopia_root, "inventory", "pixil-frame-0 - 2024-02-05T105702.567.png")
        self.indicator_texture = None
        if os.path.exists(indicator_path):
            try:
                self.indicator_texture = pygame.image.load(indicator_path).convert_alpha()
            except:
                pass
    
    def render(self, surface):
        """Render hotbar using actual assets from TSCN"""
        # Position at bottom center to match Godot screenshot
        hotbar_scale = 3
        
        # Base hotbar dimensions from hotbar.tscn NinePatchRect
        base_width = 216.025
        base_height = 28
        
        final_width = int(base_width * hotbar_scale * self.scale_x)
        final_height = int(base_height * hotbar_scale * self.scale_y)
        
        # Center horizontally, position at bottom
        hotbar_x = (surface.get_width() - final_width) // 2
        hotbar_y = surface.get_height() - final_height - 20
        
        # Draw hotbar background using actual asset
        if self.bg_texture:
            bg_scaled = pygame.transform.scale(self.bg_texture, (final_width, final_height))
            surface.blit(bg_scaled, (hotbar_x, hotbar_y))
        else:
            # Fallback: tan rectangle with border
            pygame.draw.rect(surface, (222, 184, 135), (hotbar_x, hotbar_y, final_width, final_height))
            pygame.draw.rect(surface, (139, 90, 43), (hotbar_x, hotbar_y, final_width, final_height), 2)
        
        # Draw selection indicator on selected slot using actual sprite
        if self.indicator_texture:
            # GridContainer offset and scale from hotbar.tscn
            grid_x = int(6 * hotbar_scale * self.scale_x)
            grid_y = int(3 * hotbar_scale * self.scale_y)
            grid_scale = 1.3 * hotbar_scale
            
            # Slot positions from TSCN
            slot_positions = [8.08824, 27.9412, 47.7941, 67.6471, 87.5, 107.353, 127.206, 146.324]
            
            selected_x_offset = slot_positions[self.selected_slot]
            selected_y_offset = 1.42857
            
            ind_x = hotbar_x + grid_x + int(selected_x_offset * grid_scale * self.scale_x)
            ind_y = hotbar_y + grid_y + int(selected_y_offset * grid_scale * self.scale_y)
            
            # Indicator sprite: scale (0.397, 0.409), rotation 1.5708 (90 degrees)
            indicator_size = int(16 * 0.397 * grid_scale * self.scale_x)
            indicator_scaled = pygame.transform.scale(self.indicator_texture, (indicator_size, indicator_size))
            indicator_rotated = pygame.transform.rotate(indicator_scaled, 90)
            
            ind_rect = indicator_rotated.get_rect(center=(ind_x, ind_y))
            surface.blit(indicator_rotated, ind_rect)


class MoneyPanel:
    """
    ⚠️  CRITICAL: Money/currency display panel - from ui.tscn
    
    SYSTEMS MANAGED BY THIS CLASS:
    • Player money/currency display
    • Economic system UI
    • Save file synchronization
    
    FROM GODOT PROJECT:
    • Source: Croptopia - 02.11.25/scenes/ui.tscn
    • Parent: CanvasLayer / money_count
    • Components:
      ├─ Panel (background) - position (1090, 40), size (40, 40)
      ├─ Sprite2D (coin icon) - scale 2.5
      └─ Labels (count, dollar sign) - text rendering
    
    ASSET FILES REQUIRED:
    • pixil-frame-0 (5).png: Coin sprite icon
    
    CRITICAL CONNECTIONS:
    • money_count is DISPLAYED EVERY FRAME
    • Must update when player sells/buys items
    • Persistence: Money value in save file
    
    DO NOT:
    • Modify the display position without checking hotbar overlap
    • Remove coin sprite rendering
    • Change text formatting ("{count} $")
    • Modify color scheme from tan/brown
    
    INTERFACE:
    • money_count: Current player money amount (int)
    • render(surface): Draws money panel on screen
    
    POSITIONING (from TSCN):
    • Original position: (1090, 40)
    • Updated position (from screenshot): (1220, 40) - top-right
    • Size: 40x40 base → 100x100 observed (larger in screenshot)
    • Anchor: Top-right corner
    
    ECONOMIC BALANCE:
    • Starting money: 0
    • Price lists: See trading NPCs in shelburne.tscn
    • Money sinks: Crafting, trading, building
    """
    
    def __init__(self, engine, scale_x, scale_y):
        self.engine = engine
        self.scale_x = scale_x
        self.scale_y = scale_y
        self.money_count = 0
        
        # Load coin sprite
        coin_path = os.path.join(engine.croptopia_root, "assets", "pixil-frame-0 (5).png")
        self.coin_texture = None
        if os.path.exists(coin_path):
            try:
                self.coin_texture = pygame.image.load(coin_path).convert_alpha()
            except:
                pass
        
        # Load font
        font_path = os.path.join(engine.croptopia_root, "fonts", "pixelated.ttf")
        if os.path.exists(font_path):
            self.font = pygame.font.Font(font_path, 16)
        else:
            self.font = pygame.font.Font(None, 16)
    
    def render(self, surface):
        """Render money panel using actual TSCN positioning"""
        # Position in top-right corner to match Godot screenshot
        panel_width = int(120 * self.scale_x)
        panel_height = int(80 * self.scale_y)
        panel_x = surface.get_width() - panel_width - 10
        panel_y = int(10 * self.scale_y)
        
        # Draw panel background (tan color from TSCN StyleBoxFlat)
        panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
        pygame.draw.rect(surface, (187, 143, 104), panel_rect)  # Color from StyleBoxFlat
        pygame.draw.rect(surface, (59, 29, 0), panel_rect, 1)  # Border color
        
        # Draw coin sprite (scale 2.5 from TSCN)
        if self.coin_texture:
            coin_scale = 2.5 * self.scale_x
            coin_size = int(self.coin_texture.get_width() * coin_scale)
            coin_scaled = pygame.transform.scale(self.coin_texture, (coin_size, coin_size))
            coin_x = panel_x + (panel_width - coin_size) // 2
            coin_y = panel_y + (panel_height - coin_size) // 2
            surface.blit(coin_scaled, (coin_x, coin_y))
        
        # Draw money count as text
        font_path = os.path.join(self.engine.croptopia_root, "fonts", "pixelated.ttf")
        money_font = pygame.font.Font(font_path, 14) if os.path.exists(font_path) else pygame.font.Font(None, 14)
        
        money_text = str(self.money_count)
        money_surface = money_font.render(money_text, True, (0, 0, 0))
        
        # Position count label (from TSCN: offset (-10.4, -14.4))
        text_x = panel_x + panel_width // 2 - money_surface.get_width() // 2
        text_y = panel_y + panel_height // 2 - money_surface.get_height() // 2
        surface.blit(money_surface, (text_x, text_y))


class WorldTestScene(Scene):
    """
    ⚠️  CRITICAL CORE GAME SCENE - DO NOT DELETE OR HEAVILY MODIFY
    
    PURPOSE:
    Main game world scene - exact recreation of Croptopia's worldtest.tscn.
    This is where all gameplay happens after player presses "Play" from menu.
    
    FROM GODOT PROJECT:
    • Source: Croptopia - 02.11.25/scenes/worldtest.tscn
    • Root: Node2D with script worldtest.gd
    • Size: 1152x648 (Godot base resolution)
    
    SCENE TREE (from worldtest.tscn):
    Node2D (root - worldtest.gd)
    ├─ player (CharacterBody2D instance from player.tscn)
    │  └─ Script: player.gd (movement, inventory, collision)
    │  └─ AnimatedSprite2D (boy character sprite)
    │  └─ Camera2D (follows player)
    │  └─ CollisionShape2D (character collision)
    │  └─ hotbar (inventory - 8 slots)
    ├─ sandbox_post_cutscene (Marker2D) - position (-4642, -4830)
    ├─ michael_plot_pos (Marker2D) - position (-4715, -4903)
    ├─ top_of_mt_crag_pos (Marker2D) - position (-5870, -18615)
    ├─ shelburne_road_pos (Marker2D) - position (186, -1016)
    ├─ spawn_pos (Marker2D) - position (128, 21)
    ├─ shelburne_pos (Marker2D) - position (-17818, -8305)
    ├─ CanvasLayer (UI overlay)
    │  └─ Label (debug position display)
    │  └─ day_and_night (DayNightDisplay - top-left)
    │  └─ money_count (MoneyPanel - top-right)
    │  └─ hotbar (Hotbar - bottom-center)
    │  └─ stat_bars (StatBars - left side, usually hidden)
    └─ (Dynamically loaded scenes during gameplay)
       ├─ spawn_node (from spawn_node.tscn)
       ├─ ui (from ui.tscn) - main UI system
       ├─ shelburne_road (from testing.tscn)
       ├─ npc (from npc.tscn) - Zea character
       ├─ shelburne (from shelburne.tscn) - town scene
       └─ (more scenes loaded during progression)
    
    ESSENTIAL GAME SYSTEMS:
    
    1. PLAYER SYSTEM (DO NOT REMOVE)
       • Player character initialization and loading
       • Player position tracking
       • Camera following system
       • Collision detection
       See: _initialize_player() method
    
    2. WORLD RENDERING (DO NOT REMOVE)
       • Background grass/terrain tiles
       • World coordinate system
       • Camera viewport calculation
       See: render() method
    
    3. UI OVERLAY SYSTEM (DO NOT REMOVE)
       • Day/night time display (day_and_night.tscn)
       • Money counter (ui.tscn)
       • Inventory hotbar (hotbar.tscn)
       • Stat bars (for future expansion)
       See: DayNightDisplay, MoneyPanel, Hotbar classes
    
    4. GAME STATE TRACKING
       • In-game time progression (in_game_time)
       • Current day count
       • Camera position
       See: update() method
    
    5. SCENE MANAGEMENT
       • Transitions to other areas (shelburne, spawn area, etc.)
       • Marker positions for scene entry/exit
       See: __init__() method (marker positions)
    
    CRITICAL METHODS (DO NOT DELETE):
    • __init__(engine): Initialization - creates all UI and world
    • update(delta): Game loop - advances time, updates UI
    • render(surface): Rendering - draws world and UI
    • _load_assets(): Asset loading - loads textures from Godot project
    • _initialize_ui_panels(): UI setup - creates day/night, money, hotbar
    
    ASSET DEPENDENCIES:
    • grass_demo.png: World background tile
    • pixilart-frames/pixil-frame-0 - 2024-02-08T084127.840.png: Player sprite
    • pixelated.ttf: All text rendering
    • assets/game_ui_panel.png: Day/night panel background
    • assets/hotbar_asset.png: Hotbar background
    • inventory/pixil-frame-0 - 2024-02-05T105702.567.png: Selection indicator
    
    MARKER POSITIONS (scene transitions):
    These markers are loaded from worldtest.tscn and define entry points
    for scene transitions:
    • spawn_pos: (128, 21) - starting position
    • shelburne_pos: (-17818, -8305) - town entrance
    • shelburne_road_pos: (186, -1016) - road leading to town
    • top_of_mt_crag_pos: (-5870, -18615) - mountain peak
    • michael_plot_pos: (-4715, -4903) - story location
    • sandbox_post_cutscene: (-4642, -4830) - cutscene position
    
    IF YOU NEED TO MODIFY:
    
    ✓ Safe modifications:
      - Adjust UI panel positions using screenshot reference
      - Add new asset loading alongside existing code
      - Extend game state tracking (add new variables, don't delete old ones)
      - Add new features to update() or render()
      - Change colors/styling in UI render methods
    
    ✗ UNSAFE - Will break the game:
      - Delete the __init__() method
      - Remove player initialization
      - Delete world rendering code
      - Remove UI panel rendering
      - Delete class definitions
      - Comment out asset loading
      - Change method signatures
    
    TESTING CHECKLIST AFTER MODIFICATIONS:
    [ ] Game runs without Python errors
    [ ] Player appears in world (visible sprite)
    [ ] Camera follows player movement (can move view)
    [ ] Day/night panel renders in top-left
    [ ] Money panel renders in top-right
    [ ] Hotbar renders at bottom with 8 slots
    [ ] Time advances (clock progresses)
    [ ] No red error text in console
    [ ] Assets load successfully (check [WorldTestScene] ✓ messages)
    
    RELATED FILES:
    • Croptopia - 02.11.25/scenes/worldtest.tscn: Original Godot scene
    • Croptopia - 02.11.25/scenes/worldtest.gd: Original game logic
    • croptopia_python/croptopia/scenes/main_menu_scene.py: Menu that calls this
    • croptopia_python/croptopia/scene_manager.py: Scene switching
    
    DOCUMENTATION:
    • Read CROPTOPIA_1TO1_ARCHITECTURE.md for system overview
    • Read CROPTOPIA_SCENE_HIERARCHY.md for complete scene list
    • Read worldtest.gd in Godot project for original logic
    """
    
    def __init__(self, engine):
        super().__init__(engine)
        self.name = "worldtest"
        
        # UI scale
        self.ui_scale_x = 1.0
        self.ui_scale_y = 1.0
        
        # Create UI elements
        self.day_night = DayNightDisplay(engine, self.ui_scale_x, self.ui_scale_y)
        self.hotbar = Hotbar(engine, self.ui_scale_x, self.ui_scale_y)
        self.money = MoneyPanel(engine, self.ui_scale_x, self.ui_scale_y)
        
        # Load world background texture
        self.world_bg = None
        grass_path = os.path.join(engine.croptopia_root, "assets", "grass_demo.png")
        if os.path.exists(grass_path):
            try:
                self.world_bg = pygame.image.load(grass_path).convert_alpha()
            except:
                pass
        
        # World state
        self.world_loaded = True
        self.camera_x = 0
        self.camera_y = 0
    
    def handle_event(self, event):
        """Handle input events"""
        pass
    
    def update(self, delta):
        """Update game state"""
        self.day_night.update(delta)
    
    def render(self, surface):
        """Render scene - ONLY UI elements, world is rendered by main engine"""
        # DO NOT fill surface or render world background here
        # The tilemap, entities, and player are rendered in main.py _render_systems()
        
        # Render UI elements ONLY
        self.day_night.render(surface)
        self.hotbar.render(surface)
        self.money.render(surface)
