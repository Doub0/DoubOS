"""
Compare button positions across ENTIRE image, not just bottom corner
"""
from PIL import Image
import numpy as np

print('='*70)
print('FULL IMAGE BUTTON POSITION COMPARISON')
print('='*70)
print()

# Load images
ref = Image.open(r'C:\Users\Jonas\Documents\doubOS\DoubOS\reference_do_not_modify.png').convert('RGB')
screenshot = Image.open(r'C:\Users\Jonas\Documents\doubOS\DoubOS\screenshot_menu_surface.png').convert('RGB')

ref_arr = np.array(ref)

# Extract game window from reference
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

# Detect yellow-orange in FULL reference image
r_r, g_r, b_r = ref_scaled[:,:,0], ref_scaled[:,:,1], ref_scaled[:,:,2]
yellow_mask = (r_r > 200) & (g_r > 180) & (g_r < 255) & (b_r < 120)

# Detect orange in FULL screenshot
r_s, g_s, b_s = ss_arr[:,:,0], ss_arr[:,:,1], ss_arr[:,:,2]
orange_mask = (r_s > 200) & (g_s > 100) & (g_s < 180) & (b_s < 100)

y_ref, x_ref = np.where(yellow_mask)
y_ss, x_ss = np.where(orange_mask)

print('REFERENCE (yellow-orange) buttons:')
print(f'  Pixels: {len(x_ref):,}')
print(f'  Top-left: ({np.min(x_ref)}, {np.min(y_ref)})')
print(f'  Bottom-right: ({np.max(x_ref)}, {np.max(y_ref)})')
print(f'  Size: {np.max(x_ref)-np.min(x_ref)+1}x{np.max(y_ref)-np.min(y_ref)+1}')
print()

print('SCREENSHOT (orange) buttons:')
print(f'  Pixels: {len(x_ss):,}')
print(f'  Top-left: ({np.min(x_ss)}, {np.min(y_ss)})')
print(f'  Bottom-right: ({np.max(x_ss)}, {np.max(y_ss)})')
print(f'  Size: {np.max(x_ss)-np.min(x_ss)+1}x{np.max(y_ss)-np.min(y_ss)+1}')
print()

# Calculate offset to move screenshot buttons to match reference
ref_top_left = (np.min(x_ref), np.min(y_ref))
ss_top_left = (np.min(x_ss), np.min(y_ss))

offset_x = ref_top_left[0] - ss_top_left[0]
offset_y = ref_top_left[1] - ss_top_left[1]

print('='*70)
print('OFFSET TO MATCH REFERENCE')
print('='*70)
print(f'Reference top-left: {ref_top_left}')
print(f'Screenshot top-left: {ss_top_left}')
print()
print(f'X offset: {offset_x:+d} pixels (ref_x - screenshot_x)')
print(f'Y offset: {offset_y:+d} pixels (ref_y - screenshot_y)')
print()

print('TO FIX: Add these offsets to current button positions:')
print(f'  play: pygame.Rect(54{offset_x:+d}, 27{offset_y:+d}, 287, 205)')
print(f'  settings: pygame.Rect(12{offset_x:+d}, 27{offset_y:+d}, 372, 204)')
print(f'  exit: pygame.Rect(55{offset_x:+d}, 27{offset_y:+d}, 577, 224)')
