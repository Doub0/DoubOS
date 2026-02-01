"""
Create a detailed visual comparison showing exactly what's different
"""
from PIL import Image, ImageDraw, ImageFont
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

# Create a 3-panel comparison
combined = np.zeros((648, 1152*3, 3), dtype=np.uint8)
combined[:, :1152] = ref_scaled                    # Left: Reference
combined[:, 1152:2304] = ss_arr                    # Middle: Screenshot
combined[:, 2304:] = np.abs(ref_scaled.astype(int) - ss_arr.astype(int)).astype(np.uint8)  # Right: Difference

Image.fromarray(combined).save('three_panel_comparison.png')

# Create annotated version highlighting major differences
annotated = Image.fromarray(combined)
draw = ImageDraw.Draw(annotated)

# Mark the worst difference areas
worst_areas = [
    (731, 644, 'White vs Dark'),
    (1023, 240, 'Bright vs Dark'),
    (300, 300, 'Button area'),
    (576, 550, 'Bottom UI'),
]

for x, y, label in worst_areas:
    # Draw circles on all three panels
    for panel_offset in [0, 1152, 2304]:
        draw.ellipse([panel_offset + x-10, y-10, panel_offset + x+10, y+10], outline='red', width=2)

annotated.save('annotated_comparison.png')

print('Created visual comparisons:')
print('  three_panel_comparison.png')
print('    Left: Reference')
print('    Middle: Screenshot')
print('    Right: Absolute Difference')
print()
print('  annotated_comparison.png')
print('    Same as above but with red circles marking worst mismatches')
print()

# Analyze specific problem areas in detail
print('='*70)
print('ANALYSIS OF MAJOR DIFFERENCES')
print('='*70)
print()

# Check decorative elements
print('Checking specific regions:')
print()

# Region 1: Around (731, 644) - worst mismatch
r1_ref = ref_scaled[640:648, 725:740]
r1_ss = ss_arr[640:648, 725:740]
print('Region 1: (725-740, 640-648) - worst mismatch area')
print(f'  Reference has {np.sum(r1_ref > 200)} bright pixels')
print(f'  Screenshot has {np.sum(r1_ss > 200)} bright pixels')
print(f'  Ref avg color: {np.mean(r1_ref, axis=(0,1))}')
print(f'  SS avg color: {np.mean(r1_ss, axis=(0,1))}')
print()

# Region 2: Button area
r2_ref = ref_scaled[250:400, 300:900]
r2_ss = ss_arr[250:400, 300:900]
diff_r2 = np.mean(np.abs(r2_ref.astype(int) - r2_ss.astype(int)))
print('Region 2: Button area (300-900, 250-400)')
print(f'  Average difference: {diff_r2:.2f}')
print(f'  Exact matches: {np.sum(np.all(r2_ref == r2_ss, axis=2))} / {r2_ref.shape[0]*r2_ref.shape[1]}')
print()

# Check if it's an element positioning issue or a missing element issue
print('MISSING ELEMENT DETECTION:')
# Look for white/bright pixels in reference that are dark in screenshot
bright_ref = np.sum(ref_scaled, axis=2) > 600  # Bright pixels in ref
dark_ss = np.sum(ss_arr, axis=2) < 150         # Dark pixels in screenshot
missing_bright = bright_ref & dark_ss

if np.sum(missing_bright) > 0:
    my, mx = np.where(missing_bright)
    print(f'Found {np.sum(missing_bright):,} pixels that are bright in ref but dark in screenshot')
    print(f'  X range: {np.min(mx)} to {np.max(mx)}')
    print(f'  Y range: {np.min(my)} to {np.max(my)}')
    print('  This suggests missing decorative elements or UI components')
else:
    print('No obvious missing bright elements')
