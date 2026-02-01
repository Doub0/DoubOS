"""
Pixel-by-pixel comparison between reference and current screenshot
Does NOT modify the reference image - only reads it
"""
from PIL import Image
import numpy as np

# Load reference (DO NOT MODIFY)
ref = Image.open(r'C:\Users\Jonas\Documents\doubOS\DoubOS\reference_do_not_modify.png').convert('RGB')
screenshot = Image.open(r'C:\Users\Jonas\Documents\doubOS\DoubOS\screenshot_menu_surface.png').convert('RGB')

print(f'Reference: {ref.size[0]}x{ref.size[1]}')
print(f'Screenshot: {screenshot.size[0]}x{screenshot.size[1]}')
print()

# Find the game window within the reference by detecting purple pixels
ref_arr = np.array(ref)
purple_mask = (ref_arr[:,:,0] > 100) & (ref_arr[:,:,0] < 140) & \
              (ref_arr[:,:,1] > 60) & (ref_arr[:,:,1] < 100) & \
              (ref_arr[:,:,2] > 220)

py, px = np.where(purple_mask)

if len(py) == 0:
    print("ERROR: Could not find game window in reference")
    exit(1)

top = np.min(py)
left = np.min(px)
bottom = np.max(py)
right = np.max(px)

print(f'Game window found at:')
print(f'  Position: ({left}, {top})')
print(f'  Size: {right-left+1}x{bottom-top+1}')
print()

# Extract game window (in memory only, don't save)
game_window = ref_arr[top:bottom+1, left:right+1]

# Resize to 1152x648 to match game's native resolution
if game_window.shape[0] != 648 or game_window.shape[1] != 1152:
    print(f'Scaling reference game window from {game_window.shape[1]}x{game_window.shape[0]} to 1152x648')
    game_img = Image.fromarray(game_window)
    game_img = game_img.resize((1152, 648), Image.Resampling.LANCZOS)
    game_window = np.array(game_img)
    print()

# Now compare pixel-by-pixel
ss_arr = np.array(screenshot)

print('='*60)
print('PIXEL-BY-PIXEL COMPARISON')
print('='*60)

# Calculate differences
diff_r = np.abs(game_window[:,:,0].astype(int) - ss_arr[:,:,0].astype(int))
diff_g = np.abs(game_window[:,:,1].astype(int) - ss_arr[:,:,1].astype(int))
diff_b = np.abs(game_window[:,:,2].astype(int) - ss_arr[:,:,2].astype(int))

# Average difference per pixel
diff_avg = (diff_r + diff_g + diff_b) / 3.0

total_pixels = 1152 * 648
perfect_match = np.sum(diff_avg == 0)
nearly_perfect = np.sum(diff_avg <= 5)
similar = np.sum(diff_avg <= 10)
different = np.sum(diff_avg > 10)

print(f'Total pixels: {total_pixels:,}')
print(f'  Perfect match (0 diff): {perfect_match:,} ({100*perfect_match/total_pixels:.2f}%)')
print(f'  Nearly perfect (≤5): {nearly_perfect:,} ({100*nearly_perfect/total_pixels:.2f}%)')
print(f'  Similar (≤10): {similar:,} ({100*similar/total_pixels:.2f}%)')
print(f'  Different (>10): {different:,} ({100*different/total_pixels:.2f}%)')
print()
print(f'Mean difference: {np.mean(diff_avg):.2f}')
print(f'Max difference: {np.max(diff_avg):.2f}')
print()

# Find regions with biggest differences
high_diff_mask = diff_avg > 30
if np.sum(high_diff_mask) > 0:
    hy, hx = np.where(high_diff_mask)
    print(f'Areas with major differences (>30):')
    print(f'  {np.sum(high_diff_mask):,} pixels ({100*np.sum(high_diff_mask)/total_pixels:.2f}%)')
    print(f'  Y range: {np.min(hy)}-{np.max(hy)}')
    print(f'  X range: {np.min(hx)}-{np.max(hx)}')
    print()

# Create difference visualization
diff_visualization = np.zeros((648, 1152, 3), dtype=np.uint8)
# Red = different, Green = similar
for y in range(648):
    for x in range(1152):
        d = diff_avg[y, x]
        if d == 0:
            diff_visualization[y, x] = [0, 255, 0]  # Green = perfect
        elif d <= 10:
            diff_visualization[y, x] = [0, 128, 0]  # Dark green = similar
        elif d <= 30:
            diff_visualization[y, x] = [255, 255, 0]  # Yellow = moderate
        else:
            diff_visualization[y, x] = [255, 0, 0]  # Red = very different

Image.fromarray(diff_visualization).save('diff_map.png')
print('Saved difference map to: diff_map.png')
print('  Green = perfect match')
print('  Dark green = similar (≤10 diff)')
print('  Yellow = moderate diff (≤30)')
print('  Red = major diff (>30)')
