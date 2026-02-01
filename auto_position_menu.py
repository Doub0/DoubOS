#!/usr/bin/env python3
"""
Automated screenshot comparison loop for pixel-perfect main menu positioning
"""

import os
import subprocess
import time
from PIL import Image
import numpy as np

# Paths
script_dir = os.path.dirname(os.path.abspath(__file__))
reference_path = os.path.join(script_dir, "reference_menu.png")
screenshot_path = os.path.join(script_dir, "screenshot_menu_surface.png")
main_menu_path = os.path.join(script_dir, "croptopia_python", "croptopia", "scenes", "main_menu_scene.py")

# Orange pixel detection
def detect_orange_pixels(image_array):
    """Find all orange pixels (r>170, g>70, g<150, b<90)"""
    r, g, b = image_array[:,:,0], image_array[:,:,1], image_array[:,:,2]
    mask = (r > 170) & (g > 70) & (g < 150) & (b < 90)
    return mask

def calculate_centroid(mask):
    """Calculate centroid of True pixels in mask"""
    y_coords, x_coords = np.where(mask)
    if len(x_coords) == 0:
        return None, None
    return np.mean(x_coords), np.mean(y_coords)

def scale_reference_to_800x600(ref_img):
    """Scale 1919x1079 reference to 800x600"""
    return ref_img.resize((800, 600), Image.Resampling.LANCZOS)

def get_current_button_positions(menu_file_path):
    """Extract current button positions from main_menu_scene.py"""
    with open(menu_file_path, 'r') as f:
        content = f.read()
    
    positions = {}
    lines = content.split('\n')
    
    for i, line in enumerate(lines):
        if "'play':" in line:
            # Next few lines should have the rect
            for j in range(i, min(i+5, len(lines))):
                if 'pygame.Rect(' in lines[j]:
                    # Extract pygame.Rect(x, y, w, h)
                    import re
                    match = re.search(r'pygame\.Rect\(([^)]+)\)', lines[j])
                    if match:
                        coords = [int(x.strip()) for x in match.group(1).split(',')]
                        positions['play'] = coords
                    break
        
        elif "'settings':" in line:
            for j in range(i, min(i+5, len(lines))):
                if 'pygame.Rect(' in lines[j]:
                    import re
                    match = re.search(r'pygame\.Rect\(([^)]+)\)', lines[j])
                    if match:
                        coords = [int(x.strip()) for x in match.group(1).split(',')]
                        positions['settings'] = coords
                    break
        
        elif "'exit':" in line:
            for j in range(i, min(i+5, len(lines))):
                if 'pygame.Rect(' in lines[j]:
                    import re
                    match = re.search(r'pygame\.Rect\(([^)]+)\)', lines[j])
                    if match:
                        coords = [int(x.strip()) for x in match.group(1).split(',')]
                        positions['exit'] = coords
                    break
    
    return positions

def update_button_positions(menu_file_path, new_positions):
    """Update button positions in main_menu_scene.py"""
    with open(menu_file_path, 'r') as f:
        lines = f.readlines()
    
    modified = False
    for i, line in enumerate(lines):
        if "'play':" in line:
            # Find the rect line
            for j in range(i, min(i+5, len(lines))):
                if 'pygame.Rect(' in lines[j]:
                    pos = new_positions['play']
                    lines[j] = f"                'rect': pygame.Rect({pos[0]}, {pos[1]}, {pos[2]}, {pos[3]}),\n"
                    modified = True
                    break
        
        elif "'settings':" in line:
            for j in range(i, min(i+5, len(lines))):
                if 'pygame.Rect(' in lines[j]:
                    pos = new_positions['settings']
                    lines[j] = f"                'rect': pygame.Rect({pos[0]}, {pos[1]}, {pos[2]}, {pos[3]}),\n"
                    modified = True
                    break
        
        elif "'exit':" in line:
            for j in range(i, min(i+5, len(lines))):
                if 'pygame.Rect(' in lines[j]:
                    pos = new_positions['exit']
                    lines[j] = f"                'rect': pygame.Rect({pos[0]}, {pos[1]}, {pos[2]}, {pos[3]}),\n"
                    modified = True
                    break
    
    if modified:
        with open(menu_file_path, 'w') as f:
            f.writelines(lines)
    
    return modified

def run_game_and_capture():
    """Run the game to capture a new screenshot"""
    # Delete old screenshot
    if os.path.exists(screenshot_path):
        os.remove(screenshot_path)
    
    # Run game - it will auto-capture and exit after splash
    print("  [Running game to capture screenshot...]")
    # Start game in background, wait for screenshot file to appear
    launcher_path = os.path.join(script_dir, "launcher.py")
    
    proc = subprocess.Popen(['python', launcher_path], 
                           stdout=subprocess.DEVNULL,
                           stderr=subprocess.DEVNULL)
    
    # Wait for screenshot file (max 15 seconds)
    timeout = 15
    start = time.time()
    while not os.path.exists(screenshot_path):
        time.sleep(0.2)
        if time.time() - start > timeout:
            proc.kill()
            raise TimeoutError("Screenshot not captured within timeout")
    
    # Give it a moment to finish writing
    time.sleep(0.5)
    
    # Kill the game
    proc.kill()
    proc.wait()
    
    print("  [Screenshot captured]")

def main():
    print("="*80)
    print("AUTOMATED PIXEL-PERFECT MENU POSITIONING")
    print("="*80)
    print()
    
    # Load reference
    print("Loading reference image...")
    ref_img = Image.open(reference_path).convert('RGB')
    ref_scaled = scale_reference_to_800x600(ref_img)
    ref_array = np.array(ref_scaled)
    
    # Find reference centroid
    ref_mask = detect_orange_pixels(ref_array)
    ref_cx, ref_cy = calculate_centroid(ref_mask)
    ref_count = np.sum(ref_mask)
    
    print(f"Reference centroid: ({ref_cx:.2f}, {ref_cy:.2f})")
    print(f"Reference orange pixels: {ref_count}")
    print()
    
    iteration = 0
    max_iterations = 50
    target_error = 0.5  # pixels
    damping = 0.6  # Apply 60% of calculated offset
    
    while iteration < max_iterations:
        iteration += 1
        print(f"ITERATION {iteration}")
        print("-"*80)
        
        # Get current positions
        current_pos = get_current_button_positions(main_menu_path)
        print(f"Current positions:")
        for btn, pos in current_pos.items():
            print(f"  {btn}: ({pos[0]}, {pos[1]}) size ({pos[2]}x{pos[3]})")
        
        # Capture screenshot
        run_game_and_capture()
        
        # Load and analyze screenshot
        screenshot = Image.open(screenshot_path).convert('RGB')
        screenshot_array = np.array(screenshot)
        
        # Find screenshot centroid
        screenshot_mask = detect_orange_pixels(screenshot_array)
        screenshot_cx, screenshot_cy = calculate_centroid(screenshot_mask)
        screenshot_count = np.sum(screenshot_mask)
        
        print(f"Screenshot centroid: ({screenshot_cx:.2f}, {screenshot_cy:.2f})")
        print(f"Screenshot orange pixels: {screenshot_count}")
        
        # Calculate offset
        offset_x = ref_cx - screenshot_cx
        offset_y = ref_cy - screenshot_cy
        magnitude = (offset_x**2 + offset_y**2)**0.5
        
        print(f"Offset: ({offset_x:.2f}, {offset_y:.2f})")
        print(f"Magnitude: {magnitude:.2f} pixels")
        
        # Check if we're done
        if magnitude < target_error:
            print()
            print("="*80)
            print(f"✓ PIXEL-PERFECT ACHIEVED! (error: {magnitude:.3f} pixels)")
            print("="*80)
            break
        
        # Apply damped offset to button positions
        damped_x = int(offset_x * damping)
        damped_y = int(offset_y * damping)
        
        print(f"Applying damped offset: ({damped_x}, {damped_y})")
        
        # Update all button positions
        new_positions = {}
        for btn, pos in current_pos.items():
            new_x = pos[0] + damped_x
            new_y = pos[1] + damped_y
            new_positions[btn] = [new_x, new_y, pos[2], pos[3]]
            print(f"  {btn}: ({pos[0]}, {pos[1]}) -> ({new_x}, {new_y})")
        
        # Write updates
        update_button_positions(main_menu_path, new_positions)
        print()
    
    if iteration >= max_iterations:
        print()
        print("="*80)
        print(f"⚠ Max iterations reached. Final error: {magnitude:.2f} pixels")
        print("="*80)

if __name__ == '__main__':
    main()
