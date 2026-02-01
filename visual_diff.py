"""
Visual comparison - show what's obviously different
"""
from PIL import Image
import numpy as np

print('='*70)
print('VISUAL COMPARISON: Reference vs Screenshot')
print('='*70)
print()

ref = Image.open(r'C:\Users\Jonas\Documents\doubOS\DoubOS\reference_do_not_modify.png').convert('RGB')
ss = Image.open(r'C:\Users\Jonas\Documents\doubOS\DoubOS\screenshot_menu_surface.png').convert('RGB')

print(f'Reference: {ref.size}')
print(f'Screenshot: {ss.size}')
print()

# Extract reference game window
ref_arr = np.array(ref)
purple_mask = (ref_arr[:,:,0] > 100) & (ref_arr[:,:,0] < 140) & \
              (ref_arr[:,:,1] > 60) & (ref_arr[:,:,1] < 100) & \
              (ref_arr[:,:,2] > 220)
py, px = np.where(purple_mask)
top, left = np.min(py), np.min(px)
bottom, right = np.max(py), np.max(px)

print(f'Reference game window: ({left},{top}) to ({right},{bottom})')
print(f'  Size: {right-left+1}x{bottom-top+1}')
print()

# Extract and resize
game_window = ref_arr[top:bottom+1, left:right+1]
ref_game = Image.fromarray(game_window).resize((1152, 648), Image.Resampling.LANCZOS)
ref_game_arr = np.array(ref_game)

ss_arr = np.array(ss)

# Sample key areas
print('BACKGROUND COLORS:')
print(f'  Reference (100,100): {ref_game_arr[100,100]}')
print(f'  Screenshot (100,100): {ss_arr[100,100]}')
print()

print(f'  Reference (400,400): {ref_game_arr[400,400]}')
print(f'  Screenshot (400,400): {ss_arr[400,400]}')
print()

# Check corners
print('CORNER PIXELS:')
print(f'  TL Ref: {ref_game_arr[10,10]}, SS: {ss_arr[10,10]}')
print(f'  TR Ref: {ref_game_arr[10,1140]}, SS: {ss_arr[10,1140]}')
print(f'  BL Ref: {ref_game_arr[640,10]}, SS: {ss_arr[640,10]}')
print(f'  BR Ref: {ref_game_arr[640,1140]}, SS: {ss_arr[640,1140]}')
print()

# Detect button colors
r_ref, g_ref, b_ref = ref_game_arr[:,:,0], ref_game_arr[:,:,1], ref_game_arr[:,:,2]
r_ss, g_ss, b_ss = ss_arr[:,:,0], ss_arr[:,:,1], ss_arr[:,:,2]

# Reference buttons: yellow-orange
yellow_ref = (r_ref > 200) & (g_ref > 180) & (g_ref < 255) & (b_ref < 120)
y_ref, x_ref = np.where(yellow_ref)

# Screenshot buttons: orange
orange_ss = (r_ss > 200) & (g_ss > 100) & (g_ss < 180) & (b_ss < 100)
y_ss, x_ss = np.where(orange_ss)

print('BUTTON DETECTION:')
print(f'  Reference yellow pixels: {len(x_ref):,}')
if len(x_ref) > 0:
    print(f'    Color range: R({np.min(r_ref[yellow_ref])}-{np.max(r_ref[yellow_ref])}), G({np.min(g_ref[yellow_ref])}-{np.max(g_ref[yellow_ref])}), B({np.min(b_ref[yellow_ref])}-{np.max(b_ref[yellow_ref])})')
    sample_idx = np.where(yellow_ref)
    sample_color = ref_game_arr[sample_idx[0][0], sample_idx[1][0]]
    print(f'    Sample color: {sample_color}')
print()

print(f'  Screenshot orange pixels: {len(x_ss):,}')
if len(x_ss) > 0:
    print(f'    Color range: R({np.min(r_ss[orange_ss])}-{np.max(r_ss[orange_ss])}), G({np.min(g_ss[orange_ss])}-{np.max(g_ss[orange_ss])}), B({np.min(b_ss[orange_ss])}-{np.max(b_ss[orange_ss])})')
    sample_idx = np.where(orange_ss)
    sample_color = ss_arr[sample_idx[0][0], sample_idx[1][0]]
    print(f'    Sample color: {sample_color}')
print()

# Overall difference
diff = np.abs(ref_game_arr.astype(int) - ss_arr.astype(int))
avg_diff = np.mean(diff)
median_diff = np.median(diff)

print('OVERALL PIXEL DIFFERENCE:')
print(f'  Average RGB difference: {avg_diff:.2f}')
print(f'  Median RGB difference: {median_diff:.2f}')
print(f'  Exact matches: {np.sum(np.all(ref_game_arr == ss_arr, axis=2)):,} / 746,496 ({100*np.sum(np.all(ref_game_arr == ss_arr, axis=2))/746496:.2f}%)')
