"""
Main Menu Scene - Clean implementation from screenshot reference
"""

import pygame
import os
from croptopia.scenes.base_scene import Scene


class MainMenuScene(Scene):
    """Main menu with splash animation and button layout"""
    
    def __init__(self, engine):
        super().__init__('main_menu', engine)
        self.engine = engine
        
        # Camera (from main.tscn)
        self.camera_pos = pygame.Vector2(13, -2)
        self.camera_zoom = pygame.Vector2(0.6, 0.545)
        self.screen_center = pygame.Vector2(
            self.engine.display.get_width() / 2,
            self.engine.display.get_height() / 2,
        )

        # Assets
        self.titlescreen = None
        self.play_button_icon = None
        self.settings_button_icon = None
        self.exit_button_icon = None
        self.decoration_sprite = None
        self.splash_texture = None
        
        self._load_assets()
        
        # Audio
        self.music_path = os.path.join(engine.croptopia_root, "Main_menu_.wav")
        self.music_playing = False
        
        # Menu state
        self.splash_timer = 0.0
        self.show_splash = True
        self.menu_active = False
        
        # Splash animation states
        self.self_modulate_alpha = 0.0
        self.modulate_alpha = 0.0
        self.modulate_color = (1.0, 1.0, 1.0)
        
        # Button positions from Camera2D transform of main.tscn coordinates
        # Camera at (13, -2) with zoom (0.6, 0.545)
        # World coords -> Screen coords: screen = (world - cam) * zoom + center
        # Buttons need to stay on screen (X >= 0), so offset positive
        # play: world(-985, 304) -> screen(-22, 490) -> offset to (0, 490)
        # settings: world(-551, 305) -> screen(237, 491) -> (237, 491)
        # exit: world(-35, 206) -> screen(547, 437) -> (547, 437)
        self.buttons = {
            'play': {
                'rect': pygame.Rect(0, 490, 287, 205),
                'icon': None,
            },
            'settings': {
                'rect': pygame.Rect(237, 491, 372, 204),
                'icon': None,
            },
            'exit': {
                'rect': pygame.Rect(547, 437, 577, 224),
                'icon': None,
            },
            'credits': {
                'rect': pygame.Rect(313, 550, 200, 30),
                'icon': None,
            },
        }
        
        # Text elements (positions derived from main.tscn, then rendered simply)
        self.label_text = "A game by DoubO"
        self.label_font_size = max(12, int(26 * 5.30584 * self.camera_zoom.y))
        self.label_pos = (900, 580)  # Lower right area, away from buttons
        self.croptopia_text = "CROPTOPIA\nDEMO"
        # Demo sprite world pos (343, 339) -> screen via camera transform
        demo_screen = self._world_to_screen((343, 339))
        self.croptopia_pos = demo_screen  # Will be used as topleft for blitting
        self._menu_screenshot_saved = False
        self._menu_screenshot_path = os.path.abspath(
            os.path.join(self.engine.croptopia_root, "..", "screenshot_menu_surface.png")
        )

    def _world_to_screen(self, pos):
        """Convert Godot world coords to screen coords using camera settings."""
        world = pygame.Vector2(pos)
        delta = world - self.camera_pos
        scaled = pygame.Vector2(
            delta.x * self.camera_zoom.x,
            delta.y * self.camera_zoom.y,
        )
        screen = scaled + self.screen_center
        return (int(screen.x), int(screen.y))
    
    def _load_assets(self):
        """Load all menu assets"""
        assets_dir = os.path.join(self.engine.croptopia_root, "assets")
        buttons_dir = os.path.join(self.engine.croptopia_root, "buttons")
        scenes_dir = os.path.join(self.engine.croptopia_root, "scenes")
        pixilart_dir = os.path.join(self.engine.croptopia_root, "pixilart-frames")
        
        # Load Titlescreen
        titlescreen_path = os.path.join(assets_dir, "Titlescreen.png")
        if os.path.exists(titlescreen_path):
            self.titlescreen = pygame.image.load(titlescreen_path)
            self.titlescreen = pygame.transform.scale(
                self.titlescreen, 
                (self.engine.display.get_width(), self.engine.display.get_height())
            )
            print(f"[MainMenuScene] ✓ Loaded Titlescreen.png")
        
        # Load button icons - reference pixel-perfect sizes
        play_path = os.path.join(buttons_dir, "sr25704223c58aws3.png")
        if os.path.exists(play_path):
            self.play_button_icon = pygame.image.load(play_path)
            self.play_button_icon = pygame.transform.scale(self.play_button_icon, (287, 205))
            print(f"[MainMenuScene] ✓ Loaded play button icon (287x205)")
        
        settings_path = os.path.join(buttons_dir, "sr257fe7dae1daws3.png")
        if os.path.exists(settings_path):
            self.settings_button_icon = pygame.image.load(settings_path)
            self.settings_button_icon = pygame.transform.scale(self.settings_button_icon, (372, 204))
            print(f"[MainMenuScene] ✓ Loaded settings button icon (372x204)")
        
        exit_path = os.path.join(pixilart_dir, "c7e7eeb647608e2.png")
        if os.path.exists(exit_path):
            self.exit_button_icon = pygame.image.load(exit_path)
            self.exit_button_icon = pygame.transform.scale(self.exit_button_icon, (577, 224))
            print(f"[MainMenuScene] ✓ Loaded exit button icon (577x224)")
        
        # Load decoration sprite (CROPTOPIA DEMO art)
        deco_path = os.path.join(scenes_dir, "pixil-frame-0 - 2024-02-22T210355.395.png")
        if os.path.exists(deco_path):
            deco_img = pygame.image.load(deco_path).convert_alpha()
            scale_x = 6.04 * self.camera_zoom.x
            scale_y = 3.935 * self.camera_zoom.y
            target_size = (
                max(1, int(deco_img.get_width() * scale_x)),
                max(1, int(deco_img.get_height() * scale_y)),
            )
            self.decoration_sprite = pygame.transform.scale(deco_img, target_size)
            print(f"[MainMenuScene] ✓ Loaded decoration sprite ({target_size[0]}x{target_size[1]})")
        
        # Load splash texture
        splash_path = os.path.join(self.engine.croptopia_root, "pixil-frame-0 - 2024-02-26T083114.993.png")
        if os.path.exists(splash_path):
            self.splash_texture = pygame.image.load(splash_path)
            self.splash_texture = pygame.transform.scale(self.splash_texture, (100, 100))
            print(f"[MainMenuScene] ✓ Loaded splash texture")

    def enter(self):
        """Called when scene becomes active"""
        print("[MainMenuScene] Entered main menu")
        self.splash_timer = 0.0
        self.show_splash = True
        self.menu_active = False
        self._play_music()
    
    def _play_music(self):
        """Start background music"""
        if not self.music_playing and os.path.exists(self.music_path):
            try:
                if hasattr(pygame, 'mixer') and pygame.mixer.get_init():
                    pygame.mixer.music.stop()
                    pygame.mixer.music.load(self.music_path)
                    pygame.mixer.music.set_volume(0.7)
                    pygame.mixer.music.play(-1)
                    self.music_playing = True
                    print("[MainMenuScene] ♪ Main_menu_.wav playing")
            except Exception as e:
                print(f"[MainMenuScene] Audio error: {e}")

    def update(self, delta):
        """Update menu state"""
        if self.show_splash:
            self.splash_timer += delta
            if self.splash_timer >= 2.5:
                self.show_splash = False
                self.menu_active = True
                print("[MainMenuScene] ► Timer2 timeout - menu now active")
        
        # Handle button clicks
        if self.menu_active and pygame.mouse.get_pressed()[0]:
            mouse_pos = pygame.mouse.get_pos()
            for button_name, button_data in self.buttons.items():
                if button_data['rect'].collidepoint(mouse_pos):
                    self._on_button_clicked(button_name)

    def _on_button_clicked(self, button_name):
        """Handle button click"""
        if button_name == 'play':
            print("[MainMenuScene] PLAY BUTTON")
            self.engine.scene_manager.switch_scene('spawn_node')
        elif button_name == 'settings':
            print("[MainMenuScene] SETTINGS BUTTON")
        elif button_name == 'exit':
            print("[MainMenuScene] EXIT BUTTON")
            self.engine.quit()
        elif button_name == 'credits':
            print("[MainMenuScene] CREDITS BUTTON")

    def render(self, surface):
        """Render menu"""
        # Draw titlescreen background
        if self.titlescreen:
            surface.blit(self.titlescreen, (0, 0))
        
        # Draw splash animation if active
        if self.show_splash:
            self._render_splash(surface)
        
        # Draw menu if active
        if self.menu_active:
            self._render_menu(surface)
            if not self._menu_screenshot_saved:
                try:
                    pygame.image.save(surface, self._menu_screenshot_path)
                    self._menu_screenshot_saved = True
                    print(f"[MainMenuScene] ✓ Saved menu screenshot: {self._menu_screenshot_path}")
                except Exception as e:
                    print(f"[MainMenuScene] Screenshot save error: {e}")
    
    def _render_splash(self, surface):
        """Render splash screen with animation"""
        # Gray overlay background
        gray_color = (42, 42, 42)
        gray_alpha = 255
        color_rect = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        pygame.draw.rect(color_rect, (*gray_color, gray_alpha), color_rect.get_rect())
        surface.blit(color_rect, (0, 0))
        
        # Splash animation timing
        if self.splash_timer < 2.0:
            # Phase 1: Fade in (0-2s)
            progress = self.splash_timer / 2.0
            self.self_modulate_alpha = progress
            self.modulate_alpha = progress
            self.modulate_color = (
                1.0 - progress * (1.0 - 0.470588),
                1.0 - progress * 1.0,
                1.0 - progress * (1.0 - 0.207843)
            )
        elif self.splash_timer < 2.5:
            # Phase 2: Fade out (2-2.5s)
            progress = (self.splash_timer - 2.0) / 0.5
            self.self_modulate_alpha = 1.0 - progress
            self.modulate_alpha = 1.0 - progress
            self.modulate_color = (0.470588, 0, 0.207843)
        
        # Draw splash texture
        combined_alpha = self.self_modulate_alpha * self.modulate_alpha
        texture_alpha = int(255 * combined_alpha)
        
        if texture_alpha > 0 and self.splash_texture:
            color_mod_r = int(self.modulate_color[0] * 255)
            color_mod_g = int(self.modulate_color[1] * 255)
            color_mod_b = int(self.modulate_color[2] * 255)
            
            splash_surface = self.splash_texture.copy()
            splash_surface.fill((color_mod_r, color_mod_g, color_mod_b), special_flags=pygame.BLEND_RGBA_MULT)
            splash_surface.set_alpha(texture_alpha)
            
            splash_rect = splash_surface.get_rect(center=(400, 300))
            surface.blit(splash_surface, splash_rect)
    
    def _render_menu(self, surface):
        """Render menu buttons and text"""
        # Play button
        if self.play_button_icon:
            surface.blit(self.play_button_icon, self.buttons['play']['rect'])
        else:
            pygame.draw.rect(surface, (100, 200, 100), self.buttons['play']['rect'], 3)
        
        # Settings button
        if self.settings_button_icon:
            surface.blit(self.settings_button_icon, self.buttons['settings']['rect'])
        else:
            pygame.draw.rect(surface, (200, 150, 100), self.buttons['settings']['rect'], 3)
        
        # Exit button
        if self.exit_button_icon:
            surface.blit(self.exit_button_icon, self.buttons['exit']['rect'])
        else:
            pygame.draw.rect(surface, (200, 100, 100), self.buttons['exit']['rect'], 3)
        
        # Render logo art and text elements from Godot
        try:
            # CROPTOPIA DEMO art from main.tscn Sprite2D (world pos 343, 339)
            if self.decoration_sprite:
                # Blit at topleft position to match reference rendering
                deco_rect = self.decoration_sprite.get_rect(topleft=self.croptopia_pos)
                surface.blit(self.decoration_sprite, deco_rect)
            
            # "A game by DoubO" text - at bottom right, away from buttons
            font_medium = pygame.font.Font(None, self.label_font_size)
            label_surface = font_medium.render(self.label_text, True, (180, 160, 140))
            label_rect = label_surface.get_rect(topleft=self.label_pos)
            surface.blit(label_surface, label_rect)
        except Exception as e:
            print(f"[MainMenuScene] Text render error: {e}")
    
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
