"""
PIXEL-PERFECT BUTTON REGION COMPARISON
Compare button areas pixel-by-pixel and find optimal offset
"""
from PIL import Image
import numpy as np

print('='*70)
print('BUTTON REGION PIXEL-PERFECT ANALYSIS')
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

game_window = ref_arr[top:top+1035, left:left+1793]
game_img = Image.fromarray(game_window)
game_img = game_img.resize((1152, 648), Image.Resampling.LANCZOS)
ref_scaled = np.array(game_img)

ss_arr = np.array(screenshot)

print('Testing offsets X[-50 to +50], Y[-50 to +50]...')
print()

best_match = 0
best_offset = (0, 0)

# Test different offsets
for offset_y in range(-50, 51):
    for offset_x in range(-50, 51):
        # Apply offset to screenshot
        ss_offset = np.zeros_like(ss_arr)
        
        # Calculate valid region after offset
        src_y_start = max(0, -offset_y)
        src_y_end = min(ss_arr.shape[0], ss_arr.shape[0] - offset_y)
        dst_y_start = max(0, offset_y)
        dst_y_end = dst_y_start + (src_y_end - src_y_start)
        
        src_x_start = max(0, -offset_x)
        src_x_end = min(ss_arr.shape[1], ss_arr.shape[1] - offset_x)
        dst_x_start = max(0, offset_x)
        dst_x_end = dst_x_start + (src_x_end - src_x_start)
        
        ss_offset[dst_y_start:dst_y_end, dst_x_start:dst_x_end] = \
            ss_arr[src_y_start:src_y_end, src_x_start:src_x_end]
        
        # Compare with reference
        matches = np.sum(np.all(ref_scaled == ss_offset, axis=2))
        
        if matches > best_match:
            best_match = matches
            best_offset = (offset_x, offset_y)

total_pixels = ref_scaled.shape[0] * ref_scaled.shape[1]
match_percent = 100 * best_match / total_pixels

print(f'Best offset found: X{best_offset[0]:+d}, Y{best_offset[1]:+d}')
print(f'Perfect matches: {best_match:,} / {total_pixels:,} ({match_percent:.2f}%)')
print()

if match_percent > 90:
    print('✓✓✓ PIXEL-PERFECT MATCH ✓✓✓')
elif match_percent > 80:
    print('✓✓ VERY GOOD MATCH ✓✓')
elif match_percent > 70:
    print('✓ GOOD MATCH')
else:
    print('⚠ NEEDS MORE ADJUSTMENT')

print()
print('Current button rect positions: (27, -23), (-15, -23), (28, -23)')
print(f'Apply additional offset: X{best_offset[0]:+d}, Y{best_offset[1]:+d}')
print()
print('New positions should be:')
print(f"  'play': pygame.Rect({27 + best_offset[0]}, {-23 + best_offset[1]}, 287, 205)")
print(f"  'settings': pygame.Rect({-15 + best_offset[0]}, {-23 + best_offset[1]}, 372, 204)")
print(f"  'exit': pygame.Rect({28 + best_offset[0]}, {-23 + best_offset[1]}, 577, 224)")
