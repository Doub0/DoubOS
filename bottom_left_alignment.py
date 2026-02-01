"""
Compare ACTUAL button positions in bottom-left corner
NO CENTROIDS - direct pixel comparison of button regions
"""
from PIL import Image
import numpy as np

print('='*70)
print('BOTTOM-LEFT BUTTON POSITION ANALYSIS')
print('='*70)
print()

# Load images
ref = Image.open(r'C:\Users\Jonas\Documents\doubOS\DoubOS\reference_do_not_modify.png').convert('RGB')
screenshot = Image.open(r'C:\Users\Jonas\Documents\doubOS\DoubOS\screenshot_menu_surface.png').convert('RGB')

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

ss_arr = np.array(screenshot)

print('Detecting button pixels in BOTTOM-LEFT region...')
print()

# Focus on bottom-left corner where buttons actually are
# Y: 400-648 (bottom area), X: 0-700 (left area)
button_region_y = (400, 648)
button_region_x = (0, 700)

ref_region = ref_scaled[button_region_y[0]:button_region_y[1], button_region_x[0]:button_region_x[1]]
ss_region = ss_arr[button_region_y[0]:button_region_y[1], button_region_x[0]:button_region_x[1]]

# Detect yellow-orange in reference
r_r, g_r, b_r = ref_region[:,:,0], ref_region[:,:,1], ref_region[:,:,2]
yellow_mask = (r_r > 200) & (g_r > 180) & (g_r < 255) & (b_r < 120)

# Detect orange in screenshot
r_s, g_s, b_s = ss_region[:,:,0], ss_region[:,:,1], ss_region[:,:,2]
orange_mask = (r_s > 200) & (g_s > 100) & (g_s < 180) & (b_s < 100)

y_ref, x_ref = np.where(yellow_mask)
y_ss, x_ss = np.where(orange_mask)

if len(x_ref) > 0 and len(x_ss) > 0:
    # Find BOTTOM-most and LEFT-most button pixels
    ref_bottom = button_region_y[0] + np.max(y_ref)
    ref_left = button_region_x[0] + np.min(x_ref)
    ref_top = button_region_y[0] + np.min(y_ref)
    ref_right = button_region_x[0] + np.max(x_ref)
    
    ss_bottom = button_region_y[0] + np.max(y_ss)
    ss_left = button_region_x[0] + np.min(x_ss)
    ss_top = button_region_y[0] + np.min(y_ss)
    ss_right = button_region_x[0] + np.max(x_ss)
    
    print('REFERENCE (yellow-orange) button bounds:')
    print(f'  Top-left: ({ref_left}, {ref_top})')
    print(f'  Bottom-right: ({ref_right}, {ref_bottom})')
    print(f'  Size: {ref_right-ref_left+1}x{ref_bottom-ref_top+1}')
    print()
    
    print('SCREENSHOT (orange) button bounds:')
    print(f'  Top-left: ({ss_left}, {ss_top})')
    print(f'  Bottom-right: ({ss_right}, {ss_bottom})')
    print(f'  Size: {ss_right-ss_left+1}x{ss_bottom-ss_top+1}')
    print()
    
    # Calculate offset for BOTTOM-LEFT corner alignment
    offset_x = ref_left - ss_left
    offset_y = ref_top - ss_top
    
    print('='*70)
    print('BOTTOM-LEFT CORNER OFFSET')
    print('='*70)
    print(f'X offset (left edge): {offset_x:+d} pixels')
    print(f'Y offset (top edge): {offset_y:+d} pixels')
    print()
    
    if abs(offset_x) < 2 and abs(offset_y) < 2:
        print('*** PIXEL-PERFECT ***')
    else:
        print(f'APPLY: X{offset_x:+d}, Y{offset_y:+d}')
        print()
        print('This will align the bottom-left button region properly.')
else:
    print('ERROR: No button pixels detected in bottom-left region')

# Also check exact pixel matches in button region
matches = np.sum(np.all(ref_region == ss_region, axis=2))
total = ref_region.shape[0] * ref_region.shape[1]
print()
print(f'Exact pixel matches in bottom-left region: {matches:,} / {total:,} ({100*matches/total:.2f}%)')
