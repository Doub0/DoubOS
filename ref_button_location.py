"""
Find where yellow-orange buttons ACTUALLY are in reference image
"""
from PIL import Image
import numpy as np

ref = Image.open(r'C:\Users\Jonas\Documents\doubOS\DoubOS\reference_do_not_modify.png').convert('RGB')
ref_arr = np.array(ref)

# Extract game window
purple_mask = (ref_arr[:,:,0] > 100) & (ref_arr[:,:,0] < 140) & \
              (ref_arr[:,:,1] > 60) & (ref_arr[:,:,1] < 100) & \
              (ref_arr[:,:,2] > 220)
py, px = np.where(purple_mask)
top, left = np.min(py), np.min(px)
bottom, right = np.max(py), np.max(px)

game_window = ref_arr[top:bottom+1, left:right+1]
game_img = Image.fromarray(game_window)
game_img = game_img.resize((1152, 648), Image.Resampling.LANCZOS)
ref_scaled = np.array(game_img)

# Detect yellow-orange
r, g, b = ref_scaled[:,:,0], ref_scaled[:,:,1], ref_scaled[:,:,2]
yellow_mask = (r > 200) & (g > 180) & (g < 255) & (b < 120)

y_coords, x_coords = np.where(yellow_mask)

print('='*70)
print('REFERENCE IMAGE - YELLOW-ORANGE BUTTON PIXELS')
print('='*70)
print(f'Yellow pixels detected: {len(x_coords):,}')
print(f'X range: {np.min(x_coords)} to {np.max(x_coords)}')
print(f'Y range: {np.min(y_coords)} to {np.max(y_coords)}')
print()
print(f'Top-left of button region: ({np.min(x_coords)}, {np.min(y_coords)})')
print(f'Width: {np.max(x_coords) - np.min(x_coords) + 1}')
print(f'Height: {np.max(y_coords) - np.min(y_coords) + 1}')
