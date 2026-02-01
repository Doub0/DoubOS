"""
Analyze reference image - find actual button positions and sizes
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
ref_game = Image.fromarray(game_window).resize((1152, 648), Image.Resampling.LANCZOS)
ref_game_arr = np.array(ref_game)

# Find yellow-orange buttons
r_ref, g_ref, b_ref = ref_game_arr[:,:,0], ref_game_arr[:,:,1], ref_game_arr[:,:,2]
yellow_mask = (r_ref > 200) & (g_ref > 180) & (g_ref < 255) & (b_ref < 120)

y_coords, x_coords = np.where(yellow_mask)

print('REFERENCE BUTTON REGION:')
print(f'X: {np.min(x_coords)} to {np.max(x_coords)} (width: {np.max(x_coords)-np.min(x_coords)+1})')
print(f'Y: {np.min(y_coords)} to {np.max(y_coords)} (height: {np.max(y_coords)-np.min(y_coords)+1})')
print()

# Try to find individual buttons by clustering
# Buttons are typically in the lower portion
button_region_y_start = 100
button_region_y_end = 600

y_in_region, x_in_region = np.where(yellow_mask[button_region_y_start:button_region_y_end, :])
y_in_region += button_region_y_start

if len(x_in_region) > 0:
    print(f'Buttons in lower region (y {button_region_y_start}-{button_region_y_end}):')
    print(f'  X: {np.min(x_in_region)} to {np.max(x_in_region)}')
    print(f'  Y: {np.min(y_in_region)} to {np.max(y_in_region)}')
    print()
    
    # Histogram X coordinates to find button clusters
    x_hist, x_bins = np.histogram(x_in_region, bins=100)
    peaks = np.where(x_hist > np.max(x_hist) * 0.1)[0]
    
    print(f'Potential button positions: {[x_bins[p] for p in peaks]}')
