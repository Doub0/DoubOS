"""
Comprehensive pixel-by-pixel array scanning to verify pixel-perfect match
Compares every single pixel between reference and screenshot
"""
from PIL import Image
import numpy as np

print('='*70)
print('PIXEL-PERFECT VERIFICATION - FULL ARRAY SCAN')
print('='*70)
print()

# Load reference (1919x1079 full Windows screenshot)
ref = Image.open(r'C:\Users\Jonas\Documents\doubOS\DoubOS\reference_do_not_modify.png').convert('RGB')
screenshot = Image.open(r'C:\Users\Jonas\Documents\doubOS\DoubOS\screenshot_menu_surface.png').convert('RGB')

print(f'Reference size: {ref.size[0]}x{ref.size[1]}')
print(f'Screenshot size: {screenshot.size[0]}x{screenshot.size[1]}')
print()

# Extract game window from reference
ref_arr = np.array(ref)
purple_mask = (ref_arr[:,:,0] > 100) & (ref_arr[:,:,0] < 140) & \
              (ref_arr[:,:,1] > 60) & (ref_arr[:,:,1] < 100) & \
              (ref_arr[:,:,2] > 220)
py, px = np.where(purple_mask)

if len(py) == 0:
    print("ERROR: Cannot find game window in reference")
    exit(1)

top = np.min(py)
left = np.min(px)
bottom = np.max(py)
right = np.max(px)

print(f'Game window extracted from reference:')
print(f'  Position: ({left}, {top}) to ({right}, {bottom})')
print(f'  Size: {right-left+1}x{bottom-top+1}')

# Extract and resize to 1152x648
game_window = ref_arr[top:bottom+1, left:right+1]
game_img = Image.fromarray(game_window)
game_img = game_img.resize((1152, 648), Image.Resampling.LANCZOS)
ref_scaled = np.array(game_img)

ss_arr = np.array(screenshot)

print(f'Comparing arrays: {ref_scaled.shape} vs {ss_arr.shape}')
print()

# Pixel-by-pixel array scanning
print('Scanning every pixel in the 1152x648 array...')
print()

total_pixels = 1152 * 648
differences = []

# Scan through every single pixel
for y in range(648):
    for x in range(1152):
        ref_pixel = ref_scaled[y, x]
        ss_pixel = ss_arr[y, x]
        
        # Calculate RGB difference
        diff_r = abs(int(ref_pixel[0]) - int(ss_pixel[0]))
        diff_g = abs(int(ref_pixel[1]) - int(ss_pixel[1]))
        diff_b = abs(int(ref_pixel[2]) - int(ss_pixel[2]))
        
        # Total difference
        total_diff = diff_r + diff_g + diff_b
        avg_diff = (diff_r + diff_g + diff_b) / 3.0
        
        if total_diff > 0:
            differences.append({
                'x': x,
                'y': y,
                'ref': ref_pixel,
                'ss': ss_pixel,
                'diff_r': diff_r,
                'diff_g': diff_g,
                'diff_b': diff_b,
                'total': total_diff,
                'avg': avg_diff
            })

# Statistics
perfect_match = total_pixels - len(differences)
print('='*70)
print('FULL ARRAY SCAN RESULTS')
print('='*70)
print(f'Total pixels scanned: {total_pixels:,}')
print(f'Perfect match (0 diff): {perfect_match:,} ({100*perfect_match/total_pixels:.2f}%)')
print(f'Different pixels: {len(differences):,} ({100*len(differences)/total_pixels:.2f}%)')
print()

# Categorize differences
if len(differences) > 0:
    differences_array = np.array([d['avg'] for d in differences])
    
    very_small = np.sum(differences_array <= 5)
    small = np.sum((differences_array > 5) & (differences_array <= 10))
    moderate = np.sum((differences_array > 10) & (differences_array <= 30))
    large = np.sum(differences_array > 30)
    
    print('DIFFERENCE CATEGORIES:')
    print(f'  Very small (1-5 avg diff): {very_small:,} pixels')
    print(f'  Small (6-10 avg diff): {small:,} pixels')
    print(f'  Moderate (11-30 avg diff): {moderate:,} pixels')
    print(f'  Large (>30 avg diff): {large:,} pixels')
    print()
    
    print('DIFFERENCE STATISTICS:')
    print(f'  Average difference: {np.mean(differences_array):.2f}')
    print(f'  Median difference: {np.median(differences_array):.2f}')
    print(f'  Max difference: {np.max(differences_array):.2f}')
    print(f'  Min difference: {np.min(differences_array):.2f}')
    print()
    
    # Show worst 10 pixels
    sorted_diffs = sorted(differences, key=lambda d: d['total'], reverse=True)
    print('TOP 10 WORST PIXEL MISMATCHES:')
    for i, d in enumerate(sorted_diffs[:10], 1):
        print(f"  {i}. Pixel ({d['x']},{d['y']}): "
              f"Ref[{d['ref'][0]},{d['ref'][1]},{d['ref'][2]}] vs "
              f"SS[{d['ss'][0]},{d['ss'][1]},{d['ss'][2]}] "
              f"(diff: {d['total']})")
    print()
    
    # Spatial analysis - where are the differences?
    diff_x = [d['x'] for d in differences]
    diff_y = [d['y'] for d in differences]
    
    print('SPATIAL DISTRIBUTION OF DIFFERENCES:')
    print(f'  X range: {min(diff_x)} to {max(diff_x)}')
    print(f'  Y range: {min(diff_y)} to {max(diff_y)}')
    print()
    
    # Create a heatmap of differences
    heatmap = np.zeros((648, 1152), dtype=np.float32)
    for d in differences:
        heatmap[d['y'], d['x']] = d['avg']
    
    # Convert to visual representation
    heatmap_normalized = (heatmap / np.max(heatmap) * 255).astype(np.uint8)
    heatmap_colored = np.zeros((648, 1152, 3), dtype=np.uint8)
    
    # Color code: Blue=no diff, Green=small, Yellow=moderate, Red=large
    for y in range(648):
        for x in range(1152):
            val = heatmap[y, x]
            if val == 0:
                heatmap_colored[y, x] = [0, 0, 255]  # Blue
            elif val <= 5:
                heatmap_colored[y, x] = [0, 255, 0]  # Green
            elif val <= 10:
                heatmap_colored[y, x] = [0, 255, 255]  # Cyan
            elif val <= 30:
                heatmap_colored[y, x] = [255, 255, 0]  # Yellow
            else:
                heatmap_colored[y, x] = [255, 0, 0]  # Red
    
    Image.fromarray(heatmap_colored).save('pixel_difference_heatmap.png')
    print('Saved heatmap: pixel_difference_heatmap.png')
    print('  Blue = perfect match')
    print('  Green = very small diff (≤5)')
    print('  Cyan = small diff (≤10)')
    print('  Yellow = moderate diff (≤30)')
    print('  Red = large diff (>30)')
    print()

# Final verdict
print('='*70)
print('VERDICT')
print('='*70)
if perfect_match == total_pixels:
    print('✓✓✓ ABSOLUTE PIXEL-PERFECT MATCH ✓✓✓')
    print('Every single pixel is identical!')
elif perfect_match / total_pixels >= 0.95:
    print('✓✓ NEAR PIXEL-PERFECT')
    print(f'{100*perfect_match/total_pixels:.2f}% of pixels are exact matches')
elif perfect_match / total_pixels >= 0.70:
    print('✓ GOOD MATCH')
    print(f'{100*perfect_match/total_pixels:.2f}% of pixels are exact matches')
else:
    print('⚠ NEEDS IMPROVEMENT')
    print(f'Only {100*perfect_match/total_pixels:.2f}% exact match')

if len(differences) > 0:
    avg_diff = np.mean([d['avg'] for d in differences])
    if avg_diff < 5:
        print(f'Average difference is very small: {avg_diff:.2f}')
    elif avg_diff < 15:
        print(f'Average difference is small: {avg_diff:.2f}')
    elif avg_diff < 30:
        print(f'Average difference is moderate: {avg_diff:.2f}')
    else:
        print(f'Average difference is large: {avg_diff:.2f}')
