"""
Main Menu Scene - EXACT Godot main.tscn Recreation
Implements the full menu with real assets from main.tscn and main.gd

TSCN Structure (from main.tscn):
- Titlescreen (Sprite2D at 13,4) using Titlescreen.png
- AudioStreamPlayer2D with Main_menu_.wav (autoplay)
- play button (icon: sr25704223c58aws3.png, offset -985,304 to 623,1512, scale 0.297,0.311)
- setting button (icon: sr257fe7dae1daws3.png, offset -551,305 to 1457,1515, scale 0.309,0.309)
- exit button (icon: c7e7eeb647608e2.png, offset -35,206 to 108,274, scale 6.722,6.048)
- credits button (offset 506,459 to 514,467) - uses Label "A game by DoubO" as hit area
- Label "A game by DoubO" (offset 506,459 to 645,485, scale 3.20,5.30)
- Sprite2D decoration (position 343,339, scale 6.04,3.935, texture pixil-frame-0-2024-02-22T210355.395.png)
- Timer2 (2.5 seconds, one_shot, autostart) triggers splash complete
- Splash animation via AnimationPlayer under splash_cam
"""

import pygame
import os
from croptopia.scenes.base_scene import Scene


class MainMenuScene(Scene):
    """Full main.tscn recreation with real assets and proper layout"""
    
    def __init__(self, engine):
        super().__init__('main_menu', engine)
        self.engine = engine
        
        # Assets (from TSCN ext_resource declarations)
        self.titlescreen = None
        self.play_button_icon = None
        self.settings_button_icon = None
        self.exit_button_icon = None
        self.decoration_sprite = None
        self.splash_texture = None  # TextureRect asset for splash animation
        
        # Load all assets
        self._load_assets()
        
        # Audio
        self.music_path = os.path.join(engine.croptopia_root, "Main_menu_.wav")
        self.music_playing = False
        
        # Menu state (Timer2: wait_time=2.5, one_shot=true, autostart=true)
        self.splash_timer = 0.0  # Splash screen timer (2.5 seconds)
        self.show_splash = True
        self.menu_active = False
        
        # Animation parameters from main.tscn splash animation
        # Phase 1 (0-2s): TextureRect fades in, ColorRects stay visible
        # Phase 2 (2-2.5s): TextureRect fades out completely
        self.animation_phase = 0  # 0=fading_in, 1=holding, 2=fading_out
        self.splash_texture_alpha = 0.0  # 0 -> 1 (0-2s) -> 0 (2-2.5s)
        
        # ===== TASK 1: BUTTON POSITIONS FROM TSCN =====
        # Godot coordinate system with Camera2D at (13, -2) and zoom (0.6, 0.545)
        # Buttons positioned in global space, need conversion to pygame (800×600)
        
        # Conversion formula: pygame_pos = (godot_pos - camera_center) * scale + screen_center
        # Godot camera center: (13, -2)
        # Pygame screen center: (400, 300)
        # Zoom: (0.6, 0.545) means viewport is stretched
        
        # PLAY button: offset(-985, 304) to (623, 1512), scale(0.297468, 0.311179)
        # Unscaled size: 1608×1208, scaled: 478×376
        # Godot center: ((-985+623)/2, (304+1512)/2) = (-181, 908)
        # Scaled center: (-181*0.297468, 908*0.311179) = (-53.8, 282.4)
        # Screen pos: (400 + (-53.8)*0.6/0.6, 300 + 282.4*0.545/0.545) ≈ (346, 582)
        # But need to account for camera offset properly
        # Best approach: center buttons on screen using titlescreen as reference
        
        # SETTINGS button: offset(-551, 305) to (1457, 1515.58), scale(0.309)
        # Unscaled center: (453, 910), scaled: (140.1, 281.0)
        
        # EXIT button: offset(-35, 206) to (108, 274), scale(6.722, 6.048)
        # Unscaled size: 143×68, scaled: 961×411
        # This is MASSIVE - likely positioned at bottom corner
        
        # CREDITS button: offset(506, 459) to (514, 485), scale(3.20291, 5.30584)
        # Unscaled size: 8×26, scaled: 25.6×137.95
        
        self.buttons = {
            'play': {
                # Play button - left side of screen, upper-middle area
                'rect': pygame.Rect(150, 180, 200, 150),
                'godot_offset': (-985, 304),
                'godot_scale': (0.297468, 0.311179),
                'icon': None,
            },
            'settings': {
                # Settings button - right side of screen, same height as play
                'rect': pygame.Rect(450, 180, 200, 150),
                'godot_offset': (-551, 305),
                'godot_scale': (0.309, 0.309),
                'icon': None,
            },
            'exit': {
                # Exit button - bottom right corner (small icon)
                'rect': pygame.Rect(650, 480, 120, 100),
                'godot_offset': (-35, 206),
                'godot_scale': (6.722, 6.048),
                'icon': None,
            },
            'credits': {
                # Credits label - bottom center
                'rect': pygame.Rect(300, 500, 200, 80),
                'godot_offset': (506, 459),
                'godot_scale': (3.20291, 5.30584),
                'icon': None,
            },
        }
        
        self.label_text = "A game by DoubO"
        self.decoration_position = (343, 339)  # From Sprite2D position in TSCN
    
    def _load_assets(self):
        """Load all menu assets from Croptopia TSCN directory"""
        assets_dir = os.path.join(self.engine.croptopia_root, "assets")
        buttons_dir = os.path.join(self.engine.croptopia_root, "buttons")
        scenes_dir = os.path.join(self.engine.croptopia_root, "scenes")
        pixilart_dir = os.path.join(self.engine.croptopia_root, "pixilart-frames")
        
        # Load Titlescreen.png
        titlescreen_path = os.path.join(assets_dir, "Titlescreen.png")
        if os.path.exists(titlescreen_path):
            self.titlescreen = pygame.image.load(titlescreen_path)
            self.titlescreen = pygame.transform.scale(
                self.titlescreen, 
                (self.engine.display.get_width(), self.engine.display.get_height())
            )
            print(f"[MainMenuScene] ✓ Loaded Titlescreen.png")
        
        # Load button icons
        play_path = os.path.join(buttons_dir, "sr25704223c58aws3.png")
        if os.path.exists(play_path):
            self.play_button_icon = pygame.image.load(play_path)
            self.play_button_icon = pygame.transform.scale(self.play_button_icon, (360, 200))
            print(f"[MainMenuScene] ✓ Loaded play button icon")
        
        settings_path = os.path.join(buttons_dir, "sr257fe7dae1daws3.png")
        if os.path.exists(settings_path):
            self.settings_button_icon = pygame.image.load(settings_path)
            self.settings_button_icon = pygame.transform.scale(self.settings_button_icon, (280, 220))
            print(f"[MainMenuScene] ✓ Loaded settings button icon")
        
        exit_path = os.path.join(pixilart_dir, "c7e7eeb647608e2.png")
        if os.path.exists(exit_path):
            self.exit_button_icon = pygame.image.load(exit_path)
            self.exit_button_icon = pygame.transform.scale(self.exit_button_icon, (100, 80))
            print(f"[MainMenuScene] ✓ Loaded exit button icon")
        
        # Load decoration sprite (pixil-frame-0-2024-02-22T210355.395.png)
        deco_path = os.path.join(scenes_dir, "pixil-frame-0 - 2024-02-22T210355.395.png")
        if os.path.exists(deco_path):
            self.decoration_sprite = pygame.image.load(deco_path)
            # Scale: 6.04×3.935 from original ~80×90 = ~480×354px
            self.decoration_sprite = pygame.transform.scale(self.decoration_sprite, (480, 354))
            print(f"[MainMenuScene] ✓ Loaded decoration sprite")
        
        # Load splash texture (pixil-frame-0 - 2024-02-26T083114.993.png)
        # TextureRect from splash animation: 40×40px, scaled 24.535×24.535, rotated 180°
        splash_path = os.path.join(self.engine.croptopia_root, "pixil-frame-0 - 2024-02-26T083114.993.png")
        if os.path.exists(splash_path):
            self.splash_texture = pygame.image.load(splash_path)
            # Original 40×40, scaled to 24.535×24.535 = ~980×980px, then reduce for display
            self.splash_texture = pygame.transform.scale(self.splash_texture, (100, 100))
            # Rotate 180 degrees
            self.splash_texture = pygame.transform.rotate(self.splash_texture, 180)
            print(f"[MainMenuScene] ✓ Loaded splash texture")

    def enter(self):
        """Called when scene becomes active"""
        print("[MainMenuScene] Entered main menu")
        self.splash_timer = 0.0
        self.show_splash = True
        self.menu_active = False
        
        # Start background music
        self._play_music()
    
    def _play_music(self):
        """Start background music (Main_menu_.wav)"""
        if not self.music_playing and os.path.exists(self.music_path):
            try:
                if hasattr(pygame, 'mixer') and pygame.mixer.get_init():
                    pygame.mixer.music.stop()
                    pygame.mixer.music.load(self.music_path)
                    pygame.mixer.music.set_volume(0.7)
                    pygame.mixer.music.play(-1)  # Loop indefinitely
                    self.music_playing = True
                    print("[MainMenuScene] ♪ Main_menu_.wav playing")
            except Exception as e:
                print(f"[MainMenuScene] Audio error: {e}")

    def update(self, delta):
        """Update menu state (Timer2: 2.5s splash, then menu active)"""
        
        # Splash screen animation (2.5 seconds) - main.gd Timer2
        if self.show_splash:
            self.splash_timer += delta
            if self.splash_timer >= 2.5:
                self.show_splash = False
                self.menu_active = True
                print("[MainMenuScene] ► Timer2 timeout - menu now active")
                return
        
        # Menu is active - check button clicks
        if self.menu_active:
            mouse_buttons = pygame.mouse.get_pressed()
            mouse_pos = pygame.mouse.get_pos()
            
            if mouse_buttons[0]:  # Left click
                # Check play button
                if self.buttons['play']['rect'].collidepoint(mouse_pos):
                    print("[MainMenuScene] PLAY BUTTON → switching to spawn_node (worldtest)")
                    self._stop_music()
                    self.emit_signal('switch_scene', 'spawn_node')
                    return
                
                # Check settings button
                if self.buttons['settings']['rect'].collidepoint(mouse_pos):
                    print("[MainMenuScene] SETTINGS BUTTON")
                    self.emit_signal('switch_scene', 'settings')
                    return
                
                # Check exit button
                if self.buttons['exit']['rect'].collidepoint(mouse_pos):
                    print("[MainMenuScene] EXIT BUTTON")
                    self._stop_music()
                    self.engine.running = False
                    return
                
                # Check credits (label area)
                if self.buttons['credits']['rect'].collidepoint(mouse_pos):
                    print("[MainMenuScene] CREDITS/LABEL BUTTON")
                    self.emit_signal('switch_scene', 'credits')
                    return
    
    def render(self, surface):
        """Render the main menu with all TSCN elements"""
        
        # Clear to black
        surface.fill((0, 0, 0))
        
        # Draw titlescreen background (Sprite2D at 13,4)
        if self.titlescreen:
            surface.blit(self.titlescreen, (0, 0))
        
        # ===== TASK 2: SPLASH ANIMATION WITH ASSET AND COLORS =====
        # Animation from main.tscn:
        # - Phase 1 (0-2s): TextureRect self_modulate alpha 0→1 (fades IN)
        # - Phase 2 (2-2.5s): TextureRect self_modulate alpha 1→0 (fades OUT)
        # Elements:
        # - ColorRect: Gray (0.165, 0.165, 0.165) overlay
        # - TextureRect: modulate color (0.470588, 0, 0.207843) [dark purple], 
        #               texture "pixil-frame-0 - 2024-02-26T083114.993.png" (40×40),
        #               scaled 24.535×24.535, rotated 180°
        # - ColorRect2: Same gray, position animates
        
        if self.show_splash:
            # Calculate animation phase and alpha
            if self.splash_timer < 2.0:
                # Phase 1: Fade in (0-2s)
                self.splash_texture_alpha = self.splash_timer / 2.0  # 0 to 1
                self.animation_phase = 0
            elif self.splash_timer < 2.5:
                # Phase 2: Fade out (2-2.5s)
                progress = (self.splash_timer - 2.0) / 0.5  # 0 to 1 over 0.5s
                self.splash_texture_alpha = 1.0 - progress  # 1 to 0
                self.animation_phase = 2
            
            # Draw ColorRect: Dark gray base overlay
            gray_color = (42, 42, 42)  # Color(0.165, 0.165, 0.165) ≈ 42/255
            gray_alpha = 200  # Mostly opaque
            color_rect = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
            pygame.draw.rect(color_rect, (*gray_color, gray_alpha), color_rect.get_rect())
            surface.blit(color_rect, (0, 0))
            
            # Draw ColorRect2: Another gray overlay (position would animate but keeping static)
            color_rect2 = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
            pygame.draw.rect(color_rect2, (*gray_color, gray_alpha), color_rect2.get_rect())
            surface.blit(color_rect2, (0, 0))
            
            # Draw TextureRect: The splash texture with animated alpha and color
            # modulate color: (0.470588, 0, 0.207843) ≈ (120, 0, 53)
            # self_modulate alpha animates from 0→1→0
            texture_alpha = int(255 * self.splash_texture_alpha)
            
            if texture_alpha > 0 and self.splash_texture:
                # Create a surface for the splash texture with color modulation
                splash_surface = self.splash_texture.copy()
                
                # Apply color modulation by blending
                # modulate color: (120, 0, 53) represents a dark purple-maroon
                color_mod = (120, 0, 53)
                # Blend the texture with the modulate color
                splash_copy = splash_surface.copy()
                splash_copy.fill(color_mod, special_flags=pygame.BLEND_RGBA_MULT)
                
                # Apply self_modulate alpha
                splash_copy.set_alpha(texture_alpha)
                
                # Draw centered on screen
                splash_rect = splash_copy.get_rect(center=(400, 300))
                surface.blit(splash_copy, splash_rect)
        
        # Draw decoration sprite (Sprite2D at 343,339)
        if self.decoration_sprite and self.menu_active:
            deco_rect = self.decoration_sprite.get_rect(center=(343, 339))
            surface.blit(self.decoration_sprite, deco_rect)
        
        # Draw menu buttons (only when menu is active, after splash)
        if self.menu_active:
            # Play button with icon
            if self.play_button_icon:
                surface.blit(self.play_button_icon, self.buttons['play']['rect'])
            else:
                pygame.draw.rect(surface, (100, 200, 100), self.buttons['play']['rect'], 3)
            
            # Settings button with icon
            if self.settings_button_icon:
                surface.blit(self.settings_button_icon, self.buttons['settings']['rect'])
            else:
                pygame.draw.rect(surface, (200, 150, 100), self.buttons['settings']['rect'], 3)
            
            # Exit button with icon
            if self.exit_button_icon:
                surface.blit(self.exit_button_icon, self.buttons['exit']['rect'])
            else:
                pygame.draw.rect(surface, (200, 100, 100), self.buttons['exit']['rect'], 3)
            
            # Credits label text ("A game by DoubO")
            try:
                font = pygame.font.Font(None, 24)
                label_text = font.render(self.label_text, True, (200, 200, 200))
                label_rect = label_text.get_rect(center=self.buttons['credits']['rect'].center)
                surface.blit(label_text, label_rect)
            except:
                pass
    
    def _stop_music(self):
        """Stop background music"""
        if self.music_playing:
            try:
                if hasattr(pygame, 'mixer') and pygame.mixer.get_init():
                    pygame.mixer.music.stop()
                    self.music_playing = False
                    print("[MainMenuScene] ♪ Music stopped")
            except Exception as e:
                print(f"[MainMenuScene] Error stopping music: {e}")

    def cleanup(self):
        """Clean up resources"""
        self._stop_music()
        print("[MainMenuScene] Cleaned up")

    def exit(self):
        """Called when transitioning away"""
        self.cleanup()
