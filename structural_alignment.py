"""
Smart alignment using edge detection and structural matching
Focuses on edges/structures rather than color differences
"""
from PIL import Image
import numpy as np

def sobel_edges(gray_image):
    """Compute Sobel edges manually"""
    sobel_x = np.array([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]])
    sobel_y = np.array([[-1, -2, -1], [0, 0, 0], [1, 2, 1]])
    
    # Pad image
    padded = np.pad(gray_image, 1, mode='edge')
    
    edges_x = np.zeros_like(gray_image)
    edges_y = np.zeros_like(gray_image)
    
    for i in range(gray_image.shape[0]):
        for j in range(gray_image.shape[1]):
            region = padded[i:i+3, j:j+3]
            edges_x[i, j] = np.sum(region * sobel_x)
            edges_y[i, j] = np.sum(region * sobel_y)
    
    return np.hypot(edges_x, edges_y)

print('='*70)
print('STRUCTURAL ALIGNMENT ANALYSIS')
print('='*70)
print()

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

print('Computing edge maps for structural comparison...')

# Convert to grayscale
ref_gray = np.mean(ref_scaled, axis=2).astype(np.float32)
ss_gray = np.mean(ss_arr, axis=2).astype(np.float32)

# Compute edges using manual Sobel
print('  Computing Sobel edges...')
ref_edges = sobel_edges(ref_gray)
ss_edges = sobel_edges(ss_gray)

# Threshold edges
ref_edges_binary = ref_edges > 30
ss_edges_binary = ss_edges > 30

print(f'Reference edges: {np.sum(ref_edges_binary):,} pixels')
print(f'Screenshot edges: {np.sum(ss_edges_binary):,} pixels')
print()

# Try offsets using edge correlation
print('Testing offsets using edge matching...')
best_edge_match = 0
best_edge_offset = (0, 0)

for dx in range(-20, 21):
    for dy in range(-20, 21):
        if dx == 0 and dy == 0:
            shifted_edges = ss_edges_binary
        else:
            shifted_edges = np.roll(ss_edges_binary, (dy, dx), axis=(0, 1))
        
        # Count matching edge pixels
        matches = np.sum(ref_edges_binary & shifted_edges)
        
        if matches > best_edge_match:
            best_edge_match = matches
            best_edge_offset = (dx, dy)

total_ref_edges = np.sum(ref_edges_binary)
print(f'Best edge offset: X{best_edge_offset[0]:+d}, Y{best_edge_offset[1]:+d}')
print(f'Edge match: {best_edge_match:,} / {total_ref_edges:,} ({100*best_edge_match/total_ref_edges:.2f}%)')
print()

# Now test this offset on actual pixels
print(f'Testing offset X{best_edge_offset[0]:+d}, Y{best_edge_offset[1]:+d} on actual pixels...')

if best_edge_offset != (0, 0):
    dx, dy = best_edge_offset
    shifted_ss = np.roll(ss_arr, (dy, dx), axis=(0, 1))
    
    # Count exact matches with this offset
    matches = np.sum(np.all(ref_scaled == shifted_ss, axis=2))
    total = 1152 * 648
    
    print(f'Exact pixel matches with this offset: {matches:,} / {total:,} ({100*matches/total:.2f}%)')
    
    # Compare to current (no offset)
    current_matches = np.sum(np.all(ref_scaled == ss_arr, axis=2))
    print(f'Current matches (no offset): {current_matches:,} / {total:,} ({100*current_matches/total:.2f}%)')
    
    if matches > current_matches:
        improvement = matches - current_matches
        print(f'IMPROVEMENT: +{improvement:,} pixels ({100*improvement/total:.3f}%)')
        print(f'\nRECOMMENDATION: Apply offset X{dx:+d}, Y{dy:+d}')
    else:
        print(f'This offset makes things WORSE')
        print(f'Current alignment is already optimal')
else:
    print('No offset needed - already aligned')

# Save edge visualizations
edge_overlay = np.zeros((648, 1152, 3), dtype=np.uint8)
edge_overlay[ref_edges_binary] = [255, 255, 0]  # Yellow for ref edges
edge_overlay[ss_edges_binary] = [0, 255, 255]   # Cyan for screenshot edges
edge_overlay[ref_edges_binary & ss_edges_binary] = [0, 255, 0]  # Green for matching edges

Image.fromarray(edge_overlay).save('edge_alignment_overlay.png')
print()
print('Saved edge_alignment_overlay.png')
print('  Yellow = Reference edges only')
print('  Cyan = Screenshot edges only')
print('  Green = Matching edges')
