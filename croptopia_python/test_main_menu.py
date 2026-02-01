"""
Test Main Menu Scene Implementation
Verifies main menu loading, audio, and button signal handling
"""

import sys
import os

# Add project path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pygame
from croptopia.scenes.main_menu_scene import MainMenuScene
from croptopia.signals import SignalEmitter


class MockEngine:
    """Mock engine for testing"""
    def __init__(self):
        self.player = MockPlayer()
        self.running = True
        pygame.init()
        self.display = pygame.display.set_mode((1152, 648))
        # Add croptopia_root path
        import os
        self.croptopia_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class MockPlayer:
    """Mock player for testing"""
    def __init__(self):
        self.position = (0, 0)


def test_main_menu_creation():
    """Test creating main menu scene"""
    print("[TEST] Creating main menu scene...")
    engine = MockEngine()
    menu = MainMenuScene(engine)
    
    assert menu is not None, "Failed to create main menu scene"
    assert menu.show_splash == True, "Splash screen should be active"
    assert menu.menu_active == False, "Menu should not be active during splash"
    assert menu.music_playing == False, "Music not started yet"
    
    print("  [OK] Main menu scene created successfully")
    print(f"    - Show splash: {menu.show_splash}")
    print(f"    - Menu active: {menu.menu_active}")
    print(f"    - Buttons: {list(menu.buttons.keys())}")


def test_button_definitions():
    """Test button collision regions"""
    print("\n[TEST] Verifying button definitions...")
    engine = MockEngine()
    menu = MainMenuScene(engine)
    
    buttons = menu.buttons
    expected_buttons = ['play', 'settings', 'exit', 'credits']
    
    for button_name in expected_buttons:
        assert button_name in buttons, f"Missing button: {button_name}"
        button = buttons[button_name]
        assert hasattr(button, 'contains'), f"Button {button_name} missing contains() method"
    
    print(f"  [OK] All {len(buttons)} buttons defined with collision regions")
    for name, trigger in buttons.items():
        print(f"    - {name}: center={trigger.center}, size={trigger.size}")


def test_splash_screen_timer():
    """Test splash screen timing"""
    print("\n[TEST] Testing splash screen timer...")
    engine = MockEngine()
    menu = MainMenuScene(engine)
    menu.enter()
    
    # Simulate 1 second
    menu.update(1.0)
    assert menu.show_splash == True, "Splash should still be showing at 1 second"
    assert menu.menu_active == False, "Menu should not be active yet"
    
    # Simulate another 2 seconds (total 3 seconds)
    menu.update(2.0)
    assert menu.show_splash == False, "Splash should be done after 2.5 seconds"
    assert menu.menu_active == True, "Menu should be active after splash"
    
    print("  [OK] Splash screen timing working correctly")
    print(f"    - Splash timer: {menu.splash_timer:.2f}s (threshold: 2.5s)")


def test_signal_connections():
    """Test signal connections"""
    print("\n[TEST] Testing signal connections...")
    engine = MockEngine()
    menu = MainMenuScene(engine)
    
    signal_received = []
    
    # Connect to signals
    menu.on_signal('start_game', lambda: signal_received.append('start_game'))
    menu.on_signal('quit_game', lambda: signal_received.append('quit_game'))
    menu.on_signal('open_settings', lambda: signal_received.append('open_settings'))
    menu.on_signal('show_credits', lambda: signal_received.append('show_credits'))
    
    # Emit signals
    menu.emit_signal('start_game')
    menu.emit_signal('quit_game')
    
    assert 'start_game' in signal_received, "start_game signal not received"
    assert 'quit_game' in signal_received, "quit_game signal not received"
    
    print(f"  [OK] All signals received correctly: {signal_received}")


def test_button_collision():
    """Test button collision detection"""
    print("\n[TEST] Testing button collision detection...")
    engine = MockEngine()
    menu = MainMenuScene(engine)
    menu.enter()
    
    # Skip splash screen
    menu.update(3.0)
    
    # Test play button collision
    play_button = menu.buttons['play']
    # Position inside play button (center -181, 908, size 477x376)
    test_pos = (-181, 908)
    
    assert play_button.contains(test_pos), f"Play button should contain position {test_pos}"
    
    # Position outside play button
    outside_pos = (1000, 1000)
    assert not play_button.contains(outside_pos), f"Play button should NOT contain position {outside_pos}"
    
    print("  [OK] Button collision detection working")
    print(f"    - Play button: center={play_button.center}, contains test={play_button.contains(test_pos)}")


def test_menu_workflow():
    """Test complete menu workflow"""
    print("\n[TEST] Testing complete menu workflow...")
    engine = MockEngine()
    menu = MainMenuScene(engine)
    
    signals_emitted = []
    
    def capture_signal(name):
        return lambda: signals_emitted.append(name)
    
    menu.on_signal('start_game', capture_signal('start_game'))
    menu.on_signal('quit_game', capture_signal('quit_game'))
    
    # Enter menu
    menu.enter()
    print("  - Menu entered")
    
    # Wait through splash screen
    menu.update(3.0)
    print("  - Splash screen complete, menu active")
    
    assert menu.menu_active, "Menu should be active after splash"
    print("  [OK] Menu workflow complete")


if __name__ == '__main__':
    print("=" * 60)
    print("MAIN MENU SCENE TEST SUITE")
    print("=" * 60)
    
    try:
        # Initialize pygame mixer (optional for testing)
        pygame.mixer.init()
        print("[Init] Pygame mixer initialized for audio testing\n")
    except:
        print("[Init] Pygame mixer not available (audio disabled for test)\n")
    
    test_main_menu_creation()
    test_button_definitions()
    test_splash_screen_timer()
    test_signal_connections()
    test_button_collision()
    test_menu_workflow()
    
    print("\n" + "=" * 60)
    print("ALL TESTS PASSED [OK]")
    print("=" * 60)
