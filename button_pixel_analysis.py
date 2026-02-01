"""
Pixel-perfect alignment of every orange/yellow button pixel
"""
from PIL import Image
import numpy as np

print('='*70)
print('BUTTON PIXEL ALIGNMENT ANALYSIS')
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

# Detect button-colored pixels
print('Detecting button-colored pixels...')
print()

# Reference: yellow-orange buttons
r_r, g_r, b_r = ref_scaled[:,:,0], ref_scaled[:,:,1], ref_scaled[:,:,2]
yellow_mask = (r_r > 200) & (g_r > 180) & (g_r < 255) & (b_r < 120)

# Screenshot: orange buttons
r_s, g_s, b_s = ss_arr[:,:,0], ss_arr[:,:,1], ss_arr[:,:,2]
orange_mask = (r_s > 200) & (g_s > 100) & (g_s < 180) & (b_s < 100)

y_ref, x_ref = np.where(yellow_mask)
y_ss, x_ss = np.where(orange_mask)

print(f'Reference yellow pixels: {len(x_ref):,}')
print(f'Screenshot orange pixels: {len(x_ss):,}')
print()

# Calculate centroids
cx_ref, cy_ref = np.mean(x_ref), np.mean(y_ref)
cx_ss, cy_ss = np.mean(x_ss), np.mean(y_ss)

offset_x = cx_ref - cx_ss
offset_y = cy_ref - cy_ss
magnitude = np.sqrt(offset_x**2 + offset_y**2)

print(f'Reference centroid: ({cx_ref:.2f}, {cy_ref:.2f})')
print(f'Screenshot centroid: ({cx_ss:.2f}, {cy_ss:.2f})')
print(f'Offset: ({offset_x:.2f}, {offset_y:.2f})')
print(f'Magnitude: {magnitude:.2f} pixels')
print()

# Analyze spatial distribution
print('SPATIAL DISTRIBUTION:')
print()
print('Reference yellow pixels:')
print(f'  X: {np.min(x_ref)} to {np.max(x_ref)} (range: {np.max(x_ref) - np.min(x_ref)})')
print(f'  Y: {np.min(y_ref)} to {np.max(y_ref)} (range: {np.max(y_ref) - np.min(y_ref)})')
print()
print('Screenshot orange pixels:')
print(f'  X: {np.min(x_ss)} to {np.max(x_ss)} (range: {np.max(x_ss) - np.min(x_ss)})')
print(f'  Y: {np.min(y_ss)} to {np.max(y_ss)} (range: {np.max(y_ss) - np.min(y_ss)})')
print()

# Check if offset is needed
if magnitude < 1.0:
    print('✓✓✓ ALREADY PIXEL-PERFECT ✓✓✓')
    print('All button pixels are aligned within 1 pixel tolerance')
elif magnitude < 3.0:
    print('✓✓ EXCELLENT ALIGNMENT ✓✓')
    print('Button pixels are within 3 pixel tolerance')
    print(f'\nFine adjustment recommended: X{int(round(offset_x)):+d}, Y{int(round(offset_y)):+d}')
else:
    print('⚠ ADJUSTMENT NEEDED')
    print(f'Apply offset: X{int(round(offset_x)):+d}, Y{int(round(offset_y)):+d}')

print()
print('='*70)
print('DETAILED PIXEL MATCHING ANALYSIS')
print('='*70)
print()

# For each orange pixel in screenshot, find nearest yellow pixel in reference
if len(x_ss) > 0 and len(x_ref) > 0:
    # Sample analysis (too slow to do all pixels)
    sample_size = min(1000, len(x_ss))
    sample_indices = np.random.choice(len(x_ss), sample_size, replace=False)
    
    distances = []
    for idx in sample_indices:
        x_s, y_s = x_ss[idx], y_ss[idx]
        # Find nearest yellow pixel in reference
        dist = np.sqrt((x_ref - x_s)**2 + (y_ref - y_s)**2)
        min_dist = np.min(dist)
        distances.append(min_dist)
    
    distances = np.array(distances)
    
    print(f'Sampled {sample_size} orange pixels from screenshot:')
    print(f'  Average distance to nearest yellow pixel: {np.mean(distances):.2f}')
    print(f'  Median distance: {np.median(distances):.2f}')
    print(f'  Min distance: {np.min(distances):.2f}')
    print(f'  Max distance: {np.max(distances):.2f}')
    print()
    
    # Count how many are within tolerance
    within_1px = np.sum(distances < 1.0)
    within_2px = np.sum(distances < 2.0)
    within_3px = np.sum(distances < 3.0)
    
    print(f'Pixels within tolerance:')
    print(f'  <1px: {within_1px}/{sample_size} ({100*within_1px/sample_size:.1f}%)')
    print(f'  <2px: {within_2px}/{sample_size} ({100*within_2px/sample_size:.1f}%)')
    print(f'  <3px: {within_3px}/{sample_size} ({100*within_3px/sample_size:.1f}%)')
    print()

# Create visual overlay showing button pixels
button_overlay = np.zeros((648, 1152, 3), dtype=np.uint8)
button_overlay[yellow_mask] = [255, 255, 0]  # Yellow for reference
button_overlay[orange_mask] = [255, 128, 0]  # Orange for screenshot
# Where they overlap
overlap = yellow_mask & orange_mask
button_overlay[overlap] = [0, 255, 0]  # Green for overlap

overlap_count = np.sum(overlap)
print(f'PIXEL OVERLAP:')
print(f'  Reference yellow: {len(x_ref):,}')
print(f'  Screenshot orange: {len(x_ss):,}')
print(f'  Overlapping pixels: {overlap_count:,}')
print(f'  Overlap ratio: {100*overlap_count/max(len(x_ref), len(x_ss)):.2f}%')
print()

Image.fromarray(button_overlay).save('button_pixel_overlay.png')
print('Saved button_pixel_overlay.png')
print('  Yellow = Reference yellow pixels only')
print('  Orange = Screenshot orange pixels only')
print('  Green = Perfect overlap')
