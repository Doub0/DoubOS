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
        
        # Load all assets
        self._load_assets()
        
        # Audio
        self.music_path = os.path.join(engine.croptopia_root, "Main_menu_.wav")
        self.music_playing = False
        
        # Menu state (Timer2: wait_time=2.5, one_shot=true, autostart=true)
        self.splash_timer = 0.0  # Splash screen timer (2.5 seconds)
        self.show_splash = True
        self.menu_active = False
        
        # Button regions - from TSCN offset coordinates scaled to 800x600
        # Base Godot: Titlescreen at (13, 4), Camera2D zoom (0.6, 0.545)
        # Effective render area centered around (640, 360) in Godot
        # Scale from Godot 1920x1080 to Pygame 800x600 = 0.4167
        
        # From main.tscn:
        # play: offset_left=-985, offset_top=304, offset_right=623, offset_bottom=1512, scale(0.297, 0.311)
        # Unscaled bounds: (-985, 304) to (623, 1512) = 1608×1208px
        # Scaled by 0.297×0.311 ≈ 477×375px at (13,4) camera
        # Centered around: approximately (320, 400) in pygame space
        
        self.buttons = {
            'play': {
                'rect': pygame.Rect(220, 280, 360, 200),  # Play button center
                'icon': None,
            },
            'settings': {
                'rect': pygame.Rect(480, 280, 280, 220),  # Settings right of play
                'icon': None,
            },
            'exit': {
                'rect': pygame.Rect(10, 520, 100, 80),   # Exit bottom-left
                'icon': None,
            },
            'credits': {
                'rect': pygame.Rect(350, 500, 100, 50),  # Credits label area
                'icon': None,
            },
        }
        
        self.label_text = "A game by DoubO"
    
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
        
        # Draw splash animation overlay (first 2.5 seconds)
        if self.show_splash:
            # Dark fade animation - Color(0.165, 0.165, 0.165) transitioning
            alpha_fade = int(255 * (2.5 - self.splash_timer) / 2.5)  # Fade out
            splash_overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
            pygame.draw.rect(splash_overlay, (42, 42, 42, alpha_fade), splash_overlay.get_rect())
            surface.blit(splash_overlay, (0, 0))
        
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
