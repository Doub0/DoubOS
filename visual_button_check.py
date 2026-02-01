"""
Visual check: where are the buttons NOW in the screenshot?
"""
from PIL import Image, ImageDraw
import numpy as np

screenshot = Image.open(r'C:\Users\Jonas\Documents\doubOS\DoubOS\screenshot_menu_surface.png').convert('RGB')
ss_arr = np.array(screenshot)

# Detect orange button pixels
r, g, b = ss_arr[:,:,0], ss_arr[:,:,1], ss_arr[:,:,2]
orange_mask = (r > 200) & (g > 100) & (g < 180) & (b < 100)

y_coords, x_coords = np.where(orange_mask)

if len(x_coords) > 0:
    print(f'Orange button pixels detected: {len(x_coords):,}')
    print(f'X range: {np.min(x_coords)} to {np.max(x_coords)}')
    print(f'Y range: {np.min(y_coords)} to {np.max(y_coords)}')
    print()
    print('Current button positions from main_menu_scene.py:')
    print("  'play': pygame.Rect(54, 27, 287, 205)")
    print("  'settings': pygame.Rect(12, 27, 372, 204)")
    print("  'exit': pygame.Rect(55, 27, 577, 224)")
    print()
    
    # Draw bounding box on screenshot
    img_copy = screenshot.copy()
    draw = ImageDraw.Draw(img_copy)
    
    left, top = np.min(x_coords), np.min(y_coords)
    right, bottom = np.max(x_coords), np.max(y_coords)
    
    draw.rectangle([left, top, right, bottom], outline=(0, 255, 0), width=3)
    draw.text((left, top-15), f'Actual buttons: ({left},{top})', fill=(0, 255, 0))
    
    # Show defined button positions
    draw.rectangle([54, 27, 54+287, 27+205], outline=(255, 0, 0), width=2)
    draw.text((54, 15), 'Play rect', fill=(255, 0, 0))
    
    img_copy.save('button_position_check.png')
    print('Saved visualization: button_position_check.png')
    print(f'  Green box = actual orange pixels ({left},{top}) to ({right},{bottom})')
    print(f'  Red box = play button rect from code (54,27) to (341,232)')
else:
    print('NO orange pixels detected!')
