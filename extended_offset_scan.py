"""
Extended offset scan X[-100 to +100], Y[-100 to +100]
Find the absolute best match across wider range
"""
from PIL import Image
import numpy as np

print('='*70)
print('EXTENDED OFFSET SCAN')
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

best_matches = []

print('Scanning X[-100 to +100], Y[-100 to +100]...')

# Test different offsets - wider range
for offset_y in range(-100, 101, 2):  # Step by 2 for speed
    for offset_x in range(-100, 101, 2):
        # Apply offset
        ss_offset = np.zeros_like(ss_arr)
        
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
        
        # Compare
        matches = np.sum(np.all(ref_scaled == ss_offset, axis=2))
        best_matches.append((matches, offset_x, offset_y))

# Sort by match count (descending)
best_matches.sort(reverse=True)

print(f'Top 10 best offsets:')
print()
for i, (matches, ox, oy) in enumerate(best_matches[:10]):
    percent = 100 * matches / (ref_scaled.shape[0] * ref_scaled.shape[1])
    print(f'{i+1}. X{ox:+4d}, Y{oy:+4d}: {matches:7,} matches ({percent:5.2f}%)')

best_match, best_x, best_y = best_matches[0]
print()
print('='*70)
print(f'BEST OFFSET: X{best_x:+d}, Y{best_y:+d}')
print('='*70)
print()

# Now do fine scan around best offset
print('Fine-tuning around best offset...')
fine_best = []

for offset_y in range(best_y - 4, best_y + 5):
    for offset_x in range(best_x - 4, best_x + 5):
        ss_offset = np.zeros_like(ss_arr)
        
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
        
        matches = np.sum(np.all(ref_scaled == ss_offset, axis=2))
        fine_best.append((matches, offset_x, offset_y))

fine_best.sort(reverse=True)
final_match, final_x, final_y = fine_best[0]
final_percent = 100 * final_match / (ref_scaled.shape[0] * ref_scaled.shape[1])

print(f'FINAL BEST: X{final_x:+d}, Y{final_y:+d}')
print(f'Matches: {final_match:,} / {ref_scaled.shape[0] * ref_scaled.shape[1]:,} ({final_percent:.2f}%)')
print()

print('Current positions: (27, -27), (-15, -27), (28, -27)')
print(f'Apply offset: X{final_x:+d}, Y{final_y:+d}')
print()
print('New positions:')
print(f"  'play': pygame.Rect({27 + final_x}, {-27 + final_y}, 287, 205)")
print(f"  'settings': pygame.Rect({-15 + final_x}, {-27 + final_y}, 372, 204)")
print(f"  'exit': pygame.Rect({28 + final_x}, {-27 + final_y}, 577, 224)")
