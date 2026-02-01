"""
Comprehensive pixel-perfect alignment analysis
Takes screenshot, compares every pixel to reference_do_not_modify.png
"""
from PIL import Image
import numpy as np

print('='*70)
print('COMPREHENSIVE PIXEL ALIGNMENT ANALYSIS')
print('='*70)
print()

# Step 1: Load reference and extract game window
print('Step 1: Loading reference_do_not_modify.png...')
ref = Image.open(r'C:\Users\Jonas\Documents\doubOS\DoubOS\reference_do_not_modify.png').convert('RGB')
print(f'Reference size: {ref.size[0]}x{ref.size[1]}')

ref_arr = np.array(ref)

# Find game window by detecting purple pixels
purple_mask = (ref_arr[:,:,0] > 100) & (ref_arr[:,:,0] < 140) & \
              (ref_arr[:,:,1] > 60) & (ref_arr[:,:,1] < 100) & \
              (ref_arr[:,:,2] > 220)

py, px = np.where(purple_mask)
if len(py) == 0:
    print("ERROR: Cannot find game window")
    exit(1)

top = np.min(py)
left = np.min(px)
bottom = np.max(py)
right = np.max(px)

print(f'Game window: ({left},{top}) to ({right},{bottom})')
print(f'Size: {right-left+1}x{bottom-top+1}')

# Extract and resize to 1152x648
game_window = ref_arr[top:bottom+1, left:right+1]
game_img = Image.fromarray(game_window)
game_img_resized = game_img.resize((1152, 648), Image.Resampling.LANCZOS)
ref_scaled = np.array(game_img_resized)
print('Resized to 1152x648')
print()

# Step 2: Load screenshot
print('Step 2: Loading screenshot...')
screenshot = Image.open(r'C:\Users\Jonas\Documents\doubOS\DoubOS\screenshot_menu_surface.png').convert('RGB')
print(f'Screenshot size: {screenshot.size[0]}x{screenshot.size[1]}')
ss_arr = np.array(screenshot)
print()

# Step 3: Full pixel scan to find ALL differences
print('Step 3: Scanning all 746,496 pixels...')
total_pixels = 1152 * 648
perfect_matches = 0
total_diff = 0

# Create difference map
diff_map = np.zeros((648, 1152), dtype=np.float32)

for y in range(648):
    for x in range(1152):
        ref_pixel = ref_scaled[y, x]
        ss_pixel = ss_arr[y, x]
        
        diff = abs(int(ref_pixel[0]) - int(ss_pixel[0])) + \
               abs(int(ref_pixel[1]) - int(ss_pixel[1])) + \
               abs(int(ref_pixel[2]) - int(ss_pixel[2]))
        
        diff_map[y, x] = diff / 3.0
        
        if diff == 0:
            perfect_matches += 1
        total_diff += diff

avg_diff = total_diff / (total_pixels * 3.0)
print(f'Perfect matches: {perfect_matches:,} / {total_pixels:,} ({100*perfect_matches/total_pixels:.2f}%)')
print(f'Average RGB diff per pixel: {avg_diff:.2f}')
print()

# Step 4: Detect button-specific pixels for alignment
print('Step 4: Detecting button pixels...')

# Reference: yellow-orange
r_r, g_r, b_r = ref_scaled[:,:,0], ref_scaled[:,:,1], ref_scaled[:,:,2]
yellow_ref = (r_r > 200) & (g_r > 180) & (g_r < 255) & (b_r < 120)

# Screenshot: orange
r_s, g_s, b_s = ss_arr[:,:,0], ss_arr[:,:,1], ss_arr[:,:,2]
orange_ss = (r_s > 200) & (g_s > 100) & (g_s < 180) & (b_s < 100)

y_ref, x_ref = np.where(yellow_ref)
y_ss, x_ss = np.where(orange_ss)

print(f'Reference yellow pixels: {len(x_ref):,}')
print(f'Screenshot orange pixels: {len(x_ss):,}')

if len(x_ref) > 0 and len(x_ss) > 0:
    cx_ref, cy_ref = np.mean(x_ref), np.mean(y_ref)
    cx_ss, cy_ss = np.mean(x_ss), np.mean(y_ss)
    
    button_offset_x = cx_ref - cx_ss
    button_offset_y = cy_ref - cy_ss
    button_mag = np.sqrt(button_offset_x**2 + button_offset_y**2)
    
    print(f'Button centroid offset: ({button_offset_x:.2f}, {button_offset_y:.2f})')
    print(f'Button magnitude: {button_mag:.2f} pixels')
print()

# Step 5: Try to find optimal offset by cross-correlation
print('Step 5: Finding optimal alignment offset...')

# Use a feature-rich region for matching (avoid pure background)
# Sample center region with buttons
ref_sample = ref_scaled[200:450, 200:900]
ss_sample = ss_arr[200:450, 200:900]

# Try small offsets to find best match
best_offset = (0, 0)
best_match_score = 0

print('Testing offset combinations...')
for dx in range(-10, 11):
    for dy in range(-10, 11):
        # Shift screenshot by (dx, dy) and compare
        if dx == 0 and dy == 0:
            shifted = ss_sample
        else:
            shifted = np.roll(ss_arr, (dy, dx), axis=(0, 1))[200:450, 200:900]
        
        # Count exact pixel matches
        matches = np.sum(np.all(ref_sample == shifted, axis=2))
        
        if matches > best_match_score:
            best_match_score = matches
            best_offset = (dx, dy)

total_sample = ref_sample.shape[0] * ref_sample.shape[1]
print(f'Best offset found: X{best_offset[0]:+d}, Y{best_offset[1]:+d}')
print(f'Match score: {best_match_score:,} / {total_sample:,} ({100*best_match_score/total_sample:.2f}%)')
print()

# Step 6: Detailed region analysis
print('Step 6: Analyzing specific regions...')
regions = {
    'Top-left (0,0 -> 200,200)': (0, 200, 0, 200),
    'Top-center (400,0 -> 700,200)': (0, 200, 400, 700),
    'Button area (200,200 -> 450,900)': (200, 450, 200, 900),
    'Bottom-left (450,0 -> 648,300)': (450, 648, 0, 300),
    'Bottom-right (450,800 -> 648,1152)': (450, 648, 800, 1152),
}

for name, (y1, y2, x1, x2) in regions.items():
    ref_region = ref_scaled[y1:y2, x1:x2]
    ss_region = ss_arr[y1:y2, x1:x2]
    
    matches = np.sum(np.all(ref_region == ss_region, axis=2))
    total = (y2-y1) * (x2-x1)
    avg_diff = np.mean(np.abs(ref_region.astype(int) - ss_region.astype(int)))
    
    print(f'{name}:')
    print(f'  Exact matches: {100*matches/total:.1f}%')
    print(f'  Avg difference: {avg_diff:.2f}')

print()
print('='*70)
print('RECOMMENDATION')
print('='*70)

if button_mag < 1.0:
    print('✓ Button positions are already pixel-perfect!')
else:
    print(f'⚠ Button centroid offset: {button_mag:.2f} pixels')
    print(f'   Recommended: X{int(round(button_offset_x)):+d}, Y{int(round(button_offset_y)):+d}')

print()
print(f'Cross-correlation suggests offset: X{best_offset[0]:+d}, Y{best_offset[1]:+d}')
print(f'This would improve match from {100*perfect_matches/total_pixels:.2f}% to ~{100*best_match_score/total_sample:.2f}% (in sample region)')
