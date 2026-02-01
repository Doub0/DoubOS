"""
Detailed analysis of the differences to determine what needs fixing
"""
from PIL import Image
import numpy as np

# Load both images
ref = Image.open(r'C:\Users\Jonas\Documents\doubOS\DoubOS\reference_do_not_modify.png').convert('RGB')
screenshot = Image.open(r'C:\Users\Jonas\Documents\doubOS\DoubOS\screenshot_menu_surface.png').convert('RGB')

ref_arr = np.array(ref)

# Find game window
purple_mask = (ref_arr[:,:,0] > 100) & (ref_arr[:,:,0] < 140) & \
              (ref_arr[:,:,1] > 60) & (ref_arr[:,:,1] < 100) & \
              (ref_arr[:,:,2] > 220)
py, px = np.where(purple_mask)
top, left = np.min(py), np.min(px)
bottom, right = np.max(py), np.max(px)

# Extract and resize
game_window = ref_arr[top:bottom+1, left:right+1]
game_img = Image.fromarray(game_window)
game_img = game_img.resize((1152, 648), Image.Resampling.LANCZOS)
ref_scaled = np.array(game_img)

ss_arr = np.array(screenshot)

print('='*60)
print('DETAILED ANALYSIS')
print('='*60)
print()

# Sample specific regions to understand the differences
regions = {
    'Top-left corner': (slice(0, 50), slice(0, 50)),
    'Center': (slice(300, 350), slice(550, 600)),
    'Bottom-right': (slice(598, 648), slice(1102, 1152)),
    'Button area': (slice(300, 550), slice(300, 900))
}

for name, (y_slice, x_slice) in regions.items():
    ref_region = ref_scaled[y_slice, x_slice]
    ss_region = ss_arr[y_slice, x_slice]
    
    diff = np.abs(ref_region.astype(int) - ss_region.astype(int))
    avg_diff = np.mean(diff)
    
    print(f'{name}:')
    ref_avg = np.mean(ref_region, axis=(0,1))
    ss_avg = np.mean(ss_region, axis=(0,1))
    print(f'  Ref avg color: [{ref_avg[0]:.1f}, {ref_avg[1]:.1f}, {ref_avg[2]:.1f}]')
    print(f'  Screenshot avg color: [{ss_avg[0]:.1f}, {ss_avg[1]:.1f}, {ss_avg[2]:.1f}]')
    print(f'  Avg difference: {avg_diff:.2f}')
    print()

# Analyze button positions by finding orange/yellow pixels
print('BUTTON DETECTION:')
print()

# In screenshot (our buttons are orange)
r_s, g_s, b_s = ss_arr[:,:,0], ss_arr[:,:,1], ss_arr[:,:,2]
orange_ss = (r_s > 200) & (g_s > 100) & (g_s < 180) & (b_s < 100)

if np.sum(orange_ss) > 0:
    y_ss, x_ss = np.where(orange_ss)
    print(f'Screenshot orange pixels: {np.sum(orange_ss):,}')
    print(f'  Centroid: ({np.mean(x_ss):.1f}, {np.mean(y_ss):.1f})')
    print(f'  Bounds: X[{np.min(x_ss)}-{np.max(x_ss)}], Y[{np.min(y_ss)}-{np.max(y_ss)}]')
else:
    print('Screenshot: NO ORANGE PIXELS FOUND')

print()

# In reference (buttons might be yellow-orange)
r_r, g_r, b_r = ref_scaled[:,:,0], ref_scaled[:,:,1], ref_scaled[:,:,2]

# Try different color thresholds
for name, mask in [
    ('Yellow-orange', (r_r > 200) & (g_r > 180) & (g_r < 255) & (b_r < 120)),
    ('Orange', (r_r > 200) & (g_r > 100) & (g_r < 180) & (b_r < 100)),
    ('Bright yellow', (r_r > 230) & (g_r > 200) & (b_r < 150)),
]:
    count = np.sum(mask)
    if count > 0:
        y_r, x_r = np.where(mask)
        print(f'Reference {name}: {count:,} pixels')
        print(f'  Centroid: ({np.mean(x_r):.1f}, {np.mean(y_r):.1f})')
        print(f'  Bounds: X[{np.min(x_r)}-{np.max(x_r)}], Y[{np.min(y_r)}-{np.max(y_r)}]')
        
        # Calculate offset if we have screenshot data
        if np.sum(orange_ss) > 0:
            offset_x = np.mean(x_r) - np.mean(x_ss)
            offset_y = np.mean(y_r) - np.mean(y_ss)
            print(f'  Offset from screenshot: ({offset_x:.1f}, {offset_y:.1f})')
        print()

# Check background colors
print('BACKGROUND ANALYSIS:')
# Sample background pixels (away from buttons)
bg_ref = ref_scaled[100:200, 100:200]
bg_ss = ss_arr[100:200, 100:200]

ref_bg_avg = np.mean(bg_ref, axis=(0,1))
ss_bg_avg = np.mean(bg_ss, axis=(0,1))
print(f'Reference background avg: [{ref_bg_avg[0]:.1f}, {ref_bg_avg[1]:.1f}, {ref_bg_avg[2]:.1f}]')
print(f'Screenshot background avg: [{ss_bg_avg[0]:.1f}, {ss_bg_avg[1]:.1f}, {ss_bg_avg[2]:.1f}]')
print(f'Background difference: {np.mean(np.abs(bg_ref.astype(int) - bg_ss.astype(int))):.2f}')
