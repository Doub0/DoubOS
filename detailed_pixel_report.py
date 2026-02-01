"""
Generate a detailed pixel-by-pixel comparison report
"""
from PIL import Image
import numpy as np

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

# Calculate per-pixel differences
diff = np.abs(ref_scaled.astype(int) - ss_arr.astype(int))
diff_avg = np.mean(diff, axis=2)

print('='*60)
print('DETAILED PIXEL COMPARISON REPORT')
print('='*60)
print()

# Analyze different regions
regions = {
    'Background (purple area)': (slice(0, 100), slice(0, 200)),
    'Top decoration area': (slice(0, 150), slice(400, 750)),
    'Button area (center)': (slice(250, 400), slice(200, 950)),
    'Bottom area': (slice(550, 648), slice(0, 1152)),
    'Left edge': (slice(0, 648), slice(0, 100)),
    'Right edge': (slice(0, 648), slice(1050, 1152)),
}

for name, (y_slice, x_slice) in regions.items():
    ref_region = ref_scaled[y_slice, x_slice]
    ss_region = ss_arr[y_slice, x_slice]
    diff_region = diff_avg[y_slice, x_slice]
    
    total_pixels = diff_region.size
    perfect = np.sum(diff_region == 0)
    similar = np.sum(diff_region <= 10)
    different = np.sum(diff_region > 10)
    
    print(f'{name}:')
    print(f'  Perfect: {100*perfect/total_pixels:.1f}%')
    print(f'  Similar (≤10): {100*similar/total_pixels:.1f}%')
    print(f'  Different (>10): {100*different/total_pixels:.1f}%')
    print(f'  Avg diff: {np.mean(diff_region):.2f}')
    print()

# Find the most different areas
worst_pixels = np.where(diff_avg > 50)
if len(worst_pixels[0]) > 0:
    print(f'Pixels with >50 difference: {len(worst_pixels[0]):,}')
    # Sample a few
    for i in range(min(10, len(worst_pixels[0]))):
        y, x = worst_pixels[0][i], worst_pixels[1][i]
        ref_color = ref_scaled[y, x]
        ss_color = ss_arr[y, x]
        print(f'  ({x},{y}): ref{list(ref_color)} vs ss{list(ss_color)}')
    print()

# Create a side-by-side comparison image
combined = np.zeros((648, 1152*2, 3), dtype=np.uint8)
combined[:, :1152] = ref_scaled
combined[:, 1152:] = ss_arr

Image.fromarray(combined).save('side_by_side.png')
print('Saved side-by-side comparison to: side_by_side.png')
print('  Left = Reference | Right = Screenshot')
