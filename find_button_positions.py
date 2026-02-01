"""
Read reference image, find button positions, apply them
"""
from PIL import Image, ImageDraw
import numpy as np

# Load reference
ref = Image.open(r'C:\Users\Jonas\Documents\doubOS\DoubOS\reference_do_not_modify.png').convert('RGB')
ref_arr = np.array(ref)

# Extract game window
purple_mask = (ref_arr[:,:,0] > 100) & (ref_arr[:,:,0] < 140) & \
              (ref_arr[:,:,1] > 60) & (ref_arr[:,:,1] < 100) & \
              (ref_arr[:,:,2] > 220)
py, px = np.where(purple_mask)
top, left = np.min(py), np.min(px)

game_window = ref_arr[top:top+1035, left:left+1793]
ref_game = Image.fromarray(game_window).resize((1152, 648), Image.Resampling.LANCZOS)
ref_arr = np.array(ref_game)

# Detect yellow button pixels
r, g, b = ref_arr[:,:,0], ref_arr[:,:,1], ref_arr[:,:,2]
yellow_mask = (r > 200) & (g > 180) & (g < 255) & (b < 120)

y_coords, x_coords = np.where(yellow_mask)

if len(x_coords) > 0:
    # Find bottom-left corner
    min_x = np.min(x_coords)
    max_x = np.max(x_coords)
    min_y = np.min(y_coords)
    max_y = np.max(y_coords)
    
    print('REFERENCE IMAGE ANALYSIS:')
    print(f'Button region: X {min_x}-{max_x}, Y {min_y}-{max_y}')
    print()
    
    # Try to find individual buttons by X clustering
    x_hist, x_bins = np.histogram(x_coords, bins=50)
    
    # Find peaks (button centers)
    peaks = []
    for i in range(len(x_hist)):
        if x_hist[i] > np.max(x_hist) * 0.05:  # 5% threshold
            peaks.append(x_bins[i])
    
    print(f'Button clusters found: {len(set([int(p/50) for p in peaks]))} groups')
    
    # Group X positions into 3 buttons
    play_x = min_x
    play_y = max_y - 205  # Button height 205
    
    settings_x = play_x + 287  # After play button
    settings_y = max_y - 204
    
    exit_x = settings_x + 372  # After settings button
    exit_y = max_y - 224
    
    print()
    print('CALCULATED POSITIONS (bottom-left corner):')
    print(f"  'play': pygame.Rect({play_x}, {play_y}, 287, 205),")
    print(f"  'settings': pygame.Rect({settings_x}, {settings_y}, 372, 204),")
    print(f"  'exit': pygame.Rect({exit_x}, {exit_y}, 577, 224),")
    print()
    
    # Visualize
    vis = ref_game.copy()
    draw = ImageDraw.Draw(vis)
    
    # Draw button outlines
    draw.rectangle([play_x, play_y, play_x+287, play_y+205], outline=(0, 255, 0), width=2)
    draw.text((play_x+5, play_y+5), 'PLAY', fill=(0, 255, 0))
    
    draw.rectangle([settings_x, settings_y, settings_x+372, settings_y+204], outline=(0, 255, 0), width=2)
    draw.text((settings_x+5, settings_y+5), 'SETTINGS', fill=(0, 255, 0))
    
    draw.rectangle([exit_x, exit_y, exit_x+577, exit_y+224], outline=(0, 255, 0), width=2)
    draw.text((exit_x+5, exit_y+5), 'EXIT', fill=(0, 255, 0))
    
    vis.save('button_positions_correct.png')
    print('Saved visualization: button_positions_correct.png')
