"""
ACTUAL BUTTON POSITION ANALYSIS - NO GUESSING
Compare reference to screenshot, find exact offsets needed
"""
from PIL import Image
import numpy as np

# Load both images
ref = Image.open(r'C:\Users\Jonas\Documents\doubOS\DoubOS\reference_do_not_modify.png').convert('RGB')
ss = Image.open(r'C:\Users\Jonas\Documents\doubOS\DoubOS\screenshot_menu_surface.png').convert('RGB')

ref_arr = np.array(ref)
ss_arr = np.array(ss)

# Extract game window from reference
purple_mask = (ref_arr[:,:,0] > 100) & (ref_arr[:,:,0] < 140) & \
              (ref_arr[:,:,1] > 60) & (ref_arr[:,:,1] < 100) & \
              (ref_arr[:,:,2] > 220)
py, px = np.where(purple_mask)
top, left = np.min(py), np.min(px)

game_window = ref_arr[top:top+1035, left:left+1793]
ref_scaled = Image.fromarray(game_window).resize((1152, 648), Image.Resampling.LANCZOS)
ref_arr = np.array(ref_scaled)

print('='*70)
print('TRUSTWORTHY BUTTON POSITION ANALYSIS')
print('='*70)
print()

# Detect button pixels
r_ref, g_ref, b_ref = ref_arr[:,:,0], ref_arr[:,:,1], ref_arr[:,:,2]
r_ss, g_ss, b_ss = ss_arr[:,:,0], ss_arr[:,:,1], ss_arr[:,:,2]

# Reference: yellow-orange buttons [255, 222, 102]
yellow_mask = (r_ref > 200) & (g_ref > 180) & (g_ref < 255) & (b_ref < 120)

# Screenshot: orange buttons [255, 126, 0]
orange_mask = (r_ss > 200) & (g_ss > 100) & (g_ss < 180) & (b_ss < 100)

y_ref, x_ref = np.where(yellow_mask)
y_ss, x_ss = np.where(orange_mask)

print('REFERENCE IMAGE (yellow buttons):')
print(f'  Total pixels: {len(x_ref):,}')
if len(x_ref) > 0:
    print(f'  X range: {np.min(x_ref)} to {np.max(x_ref)} (span: {np.max(x_ref)-np.min(x_ref)+1})')
    print(f'  Y range: {np.min(y_ref)} to {np.max(y_ref)} (span: {np.max(y_ref)-np.min(y_ref)+1})')
print()

print('SCREENSHOT (orange buttons):')
print(f'  Total pixels: {len(x_ss):,}')
if len(x_ss) > 0:
    print(f'  X range: {np.min(x_ss)} to {np.max(x_ss)} (span: {np.max(x_ss)-np.min(x_ss)+1})')
    print(f'  Y range: {np.min(y_ss)} to {np.max(y_ss)} (span: {np.max(y_ss)-np.min(y_ss)+1})')
print()

# Find button bounding boxes
if len(x_ref) > 0 and len(x_ss) > 0:
    # Top-left corner position
    ref_top_left = (np.min(x_ref), np.min(y_ref))
    ss_top_left = (np.min(x_ss), np.min(y_ss))
    
    # Bottom-left corner position
    ref_bottom_left = (np.min(x_ref), np.max(y_ref))
    ss_bottom_left = (np.min(x_ss), np.max(y_ss))
    
    print('TOP-LEFT CORNER (reference start):')
    print(f'  Reference: {ref_top_left}')
    print(f'  Screenshot: {ss_top_left}')
    offset_tl = (ref_top_left[0] - ss_top_left[0], ref_top_left[1] - ss_top_left[1])
    print(f'  Offset needed: X{offset_tl[0]:+d}, Y{offset_tl[1]:+d}')
    print()
    
    print('BOTTOM-LEFT CORNER (button baseline):')
    print(f'  Reference: {ref_bottom_left}')
    print(f'  Screenshot: {ss_bottom_left}')
    offset_bl = (ref_bottom_left[0] - ss_bottom_left[0], ref_bottom_left[1] - ss_bottom_left[1])
    print(f'  Offset needed: X{offset_bl[0]:+d}, Y{offset_bl[1]:+d}')
    print()
    
    # Centroid comparison
    ref_cx, ref_cy = np.mean(x_ref), np.mean(y_ref)
    ss_cx, ss_cy = np.mean(x_ss), np.mean(y_ss)
    
    offset_centroid = (ref_cx - ss_cx, ref_cy - ss_cy)
    mag = (offset_centroid[0]**2 + offset_centroid[1]**2)**0.5
    
    print('CENTROID COMPARISON (center of all buttons):')
    print(f'  Reference: ({ref_cx:.1f}, {ref_cy:.1f})')
    print(f'  Screenshot: ({ss_cx:.1f}, {ss_cy:.1f})')
    print(f'  Offset: X{offset_centroid[0]:+.1f}, Y{offset_centroid[1]:+.1f}')
    print(f'  Distance: {mag:.1f} pixels')
    print()
    
    # Apply offsets to current button positions
    current_play = (0, 442)
    current_settings = (287, 443)
    current_exit = (659, 423)
    
    print('CURRENT BUTTON POSITIONS:')
    print(f"  play: {current_play}")
    print(f"  settings: {current_settings}")
    print(f"  exit: {current_exit}")
    print()
    
    # Apply centroid offset (most reliable for overall layout)
    offset_x = int(offset_centroid[0])
    offset_y = int(offset_centroid[1])
    
    print('APPLYING CENTROID OFFSET:')
    print(f"  Offset: X{offset_x:+d}, Y{offset_y:+d}")
    print()
    print('NEW POSITIONS:')
    print(f"  'play': pygame.Rect({current_play[0]+offset_x}, {current_play[1]+offset_y}, 287, 205),")
    print(f"  'settings': pygame.Rect({current_settings[0]+offset_x}, {current_settings[1]+offset_y}, 372, 204),")
    print(f"  'exit': pygame.Rect({current_exit[0]+offset_x}, {current_exit[1]+offset_y}, 577, 224),")
