"""
Quick test to render main menu and save screenshot
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pygame
from croptopia.scenes.main_menu_scene import MainMenuScene

class MockEngine:
    """Mock engine for testing"""
    def __init__(self):
        class MockPlayer:
            def __init__(self):
                self.position = (0, 0)
        
        self.player = MockPlayer()
        self.running = True
        pygame.init()
        self.display = pygame.display.set_mode((1152, 648))
        self.croptopia_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Create the menu
engine = MockEngine()
menu = MainMenuScene(engine)

# Create a surface to render to
surface = pygame.Surface((1152, 648))
surface.fill((100, 100, 100))

# Manually trigger update and draw to skip splash
menu.show_splash = False
menu.menu_active = True

# Render a single frame
menu.update(0.016)
menu.render(surface)

# Save screenshot
screenshot_path = r"C:\Users\Jonas\Documents\doubOS\DoubOS\menu_test.png"
pygame.image.save(surface, screenshot_path)
print(f"Screenshot saved to {screenshot_path}")

# Print button rects for verification
print("\nButton positions (screen space):")
for name, button in menu.buttons.items():
    rect = button['rect']
    print(f"  {name:12} - x={rect.x:4}, y={rect.y:4}, w={rect.width:4}, h={rect.height:4}")

print("\nLabel info:")
print(f"  position: {menu.label_pos}")
print(f"  scale: {menu.label_scale}")
print(f"  base_font_size: {menu.label_base_font_size}")

pygame.quit()
