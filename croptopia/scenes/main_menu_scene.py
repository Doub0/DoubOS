"""
Main Menu Scene
Implements the menu screen with audio playback and button navigation.
Audio: Main_menu_.wav (background music)
"""

import pygame
from croptopia.scenes.base_scene import Scene, RectTrigger


class MainMenuScene(Scene):
    """Main menu scene with title screen, buttons, and background music"""
    
    def __init__(self, engine):
        super().__init__(engine)
        
        # Audio
        self.audio_path = "croptopia_assets/Main_menu_.wav"
        self.music_playing = False
        self.music_channel = None
        
        # Menu state
        self.splash_timer = 0.0  # Splash screen timer (2.5 seconds)
        self.show_splash = True
        self.menu_active = False
        
        # Button regions (approximate hit boxes based on TSCN)
        # play button: center ~(-181, 908), size ~(1608, 1208), scale (0.297, 0.311)
        # settings button: center ~(453, 910), scale (0.309, 0.309)
        # exit button: center ~(36, 240), scale (6.722, 6.048)
        # credits button: center ~(510, 463)
        
        self.buttons = {
            'play': RectTrigger(center=(-181, 908), size=(477, 376)),
            'settings': RectTrigger(center=(453, 910), size=(450, 376)),
            'exit': RectTrigger(center=(36, 240), size=(143, 68)),
            'credits': RectTrigger(center=(510, 463), size=(8, 8)),
        }

    def enter(self):
        """Called when scene becomes active"""
        print("[MainMenuScene] Entered main menu")
        self.splash_timer = 0.0
        self.show_splash = True
        self.menu_active = False
        
        # Start background music
        self._play_music()
    
    def _play_music(self):
        """Start background music playback"""
        if not self.music_playing:
            try:
                # Use pygame's mixer to play background music
                if hasattr(pygame, 'mixer') and pygame.mixer.get_init():
                    # Stop any existing music
                    pygame.mixer.music.stop()
                    
                    # Load and play Main_menu_.wav
                    pygame.mixer.music.load(self.audio_path)
                    pygame.mixer.music.set_volume(0.7)
                    pygame.mixer.music.play(-1)  # Loop indefinitely
                    self.music_playing = True
                    print("[MainMenuScene] ♪ Background music started")
            except Exception as e:
                print(f"[MainMenuScene] Audio error: {e}")

    def update(self, delta):
        """Update menu state and check for button presses"""
        
        # Splash screen timer (2.5 seconds)
        if self.show_splash:
            self.splash_timer += delta
            if self.splash_timer >= 2.5:
                self.show_splash = False
                self.menu_active = True
                print("[MainMenuScene] Splash screen complete, menu active")
                return
        
        # Menu button detection
        if self.menu_active and hasattr(self.engine, 'player') and self.engine.player:
            player_pos = self.engine.player.position
            
            # Check play button
            if self.buttons['play'].contains(player_pos):
                print("[MainMenuScene] Play button pressed")
                self._stop_music()
                self.emit_signal('start_game')
            
            # Check settings button
            if self.buttons['settings'].contains(player_pos):
                print("[MainMenuScene] Settings button pressed")
                self.emit_signal('open_settings')
            
            # Check exit button
            if self.buttons['exit'].contains(player_pos):
                print("[MainMenuScene] Exit button pressed")
                self._stop_music()
                self.emit_signal('quit_game')
            
            # Check credits button
            if self.buttons['credits'].contains(player_pos):
                print("[MainMenuScene] Credits button pressed")
                self.emit_signal('show_credits')
    
    def _stop_music(self):
        """Stop background music"""
        if self.music_playing:
            try:
                if hasattr(pygame, 'mixer') and pygame.mixer.get_init():
                    pygame.mixer.music.stop()
                    self.music_playing = False
                    print("[MainMenuScene] ♪ Background music stopped")
            except Exception as e:
                print(f"[MainMenuScene] Error stopping music: {e}")

    def cleanup(self):
        """Called when scene is being unloaded"""
        self._stop_music()
        print("[MainMenuScene] Cleaned up main menu")

    def exit(self):
        """Called when transitioning away from this scene"""
        self.cleanup()
