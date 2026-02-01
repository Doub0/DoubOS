#!/usr/bin/env python3
"""Auto-align menu buttons to match reference screenshot"""

import subprocess
import os
import re
from PIL import Image
import numpy as np
import time
import sys

def get_offset():
    """Measure offset between current and reference"""
    try:
        ref = Image.open('reference_menu.png')
        cur = Image.open('screenshot_menu_surface.png')
        
        ref_arr = np.array(ref)[:, :, :3]
        cur_arr = np.array(cur)
        
        sx = ref_arr.shape[1] / 800
        sy = ref_arr.shape[0] / 600
        
        # Orange detection
        ro = (ref_arr[:,:,0] > 170) & (ref_arr[:,:,1] > 70) & (ref_arr[:,:,1] < 150) & (ref_arr[:,:,2] < 90)
        co = (cur_arr[:,:,0] > 170) & (cur_arr[:,:,1] > 70) & (cur_arr[:,:,1] < 150) & (cur_arr[:,:,2] < 90)
        
        ry, rx = np.where(ro)
        cy, cx = np.where(co)
        
        rc = (np.mean(rx) / sx, np.mean(ry) / sy)
        cc = (np.mean(cx), np.mean(cy))
        
        offset = (rc[0] - cc[0], rc[1] - cc[1])
        return offset
    except Exception as e:
        print(f"Error measuring: {e}")
        return None

def update_positions(old_play, old_sett, old_exit, old_cred, offset_x):
    """Calculate new positions after applying offset"""
    new_play = max(0, int(round(old_play + offset_x)))
    new_sett = max(0, int(round(old_sett + offset_x)))
    new_exit = max(0, int(round(old_exit + offset_x)))
    new_cred = max(0, int(round(old_cred + offset_x)))
    return new_play, new_sett, new_exit, new_cred

def update_file(play_x, sett_x, exit_x, cred_x):
    """Update main_menu_scene.py with new button positions"""
    filepath = 'croptopia_python/croptopia/scenes/main_menu_scene.py'
    code = open(filepath, 'r').read()
    
    # Find and replace the buttons dict
    pattern = r"self\.buttons = \{[^}]*'play': \{[^}]*'rect': pygame\.Rect\((\d+), 385, 140, 100\),[^}]*'settings': \{[^}]*'rect': pygame\.Rect\((\d+), 385, 140, 100\),[^}]*'exit': \{[^}]*'rect': pygame\.Rect\((\d+), 385, 120, 100\),[^}]*'credits': \{[^}]*'rect': pygame\.Rect\((\d+), 434, 200, 30\)"
    
    # Simpler approach: just find and replace the 4 numbers
    new_buttons = f'''self.buttons = {{
            'play': {{
                'rect': pygame.Rect({play_x}, 385, 140, 100),
                'icon': None,
            }},
            'settings': {{
                'rect': pygame.Rect({sett_x}, 385, 140, 100),
                'icon': None,
            }},
            'exit': {{
                'rect': pygame.Rect({exit_x}, 385, 120, 100),
                'icon': None,
            }},
            'credits': {{
                'rect': pygame.Rect({cred_x}, 434, 200, 30),
                'icon': None,
            }},
        }}'''
    
    # Find the button section and replace
    lines = code.split('\n')
    in_buttons = False
    new_lines = []
    skip_count = 0
    
    for i, line in enumerate(lines):
        if skip_count > 0:
            skip_count -= 1
            continue
        
        if "self.buttons = {" in line:
            new_lines.append(new_buttons)
            # Skip old button lines
            j = i + 1
            while j < len(lines) and "}" not in lines[j]:
                skip_count += 1
                j += 1
            if j < len(lines):
                skip_count += 1  # Skip the closing }
        else:
            new_lines.append(line)
    
    code = '\n'.join(new_lines)
    open(filepath, 'w').write(code)

def run_game():
    """Start game and wait for screenshot"""
    if os.path.exists('screenshot_menu_surface.png'):
        os.remove('screenshot_menu_surface.png')
    
    os.chdir('croptopia_python')
    subprocess.Popen(['python', 'main.py'], 
                    stdout=subprocess.DEVNULL, 
                    stderr=subprocess.DEVNULL)
    time.sleep(7)
    subprocess.run(['taskkill', '/IM', 'python.exe', '/F'],
                  stdout=subprocess.DEVNULL,
                  stderr=subprocess.DEVNULL)
    os.chdir('..')
    time.sleep(1)

def main():
    """Main loop"""
    print("=" * 60)
    print("AUTO BUTTON ALIGNMENT")
    print("=" * 60)
    
    # Starting positions
    play_x, sett_x, exit_x, cred_x = 0, 76, 225, 305
    
    for iteration in range(1, 11):
        print(f"\n[Iteration {iteration}]")
        print(f"Current: play={play_x}, sett={sett_x}, exit={exit_x}, credits={cred_x}")
        
        # Run game and capture
        print("Running game...")
        run_game()
        
        # Measure offset
        offset = get_offset()
        if offset is None:
            print("ERROR: Could not measure offset")
            break
        
        offset_x, offset_y = offset
        print(f"Offset: ({offset_x:.1f}, {offset_y:.1f})")
        
        mag = (offset_x**2 + offset_y**2)**0.5
        print(f"Magnitude: {mag:.2f}px")
        
        # Check if converged
        if mag < 0.5:
            print("\n✓ CONVERGED! Buttons are pixel-perfect.")
            break
        
        # Apply offset
        play_x, sett_x, exit_x, cred_x = update_positions(
            play_x, sett_x, exit_x, cred_x, offset_x
        )
        
        print(f"New: play={play_x}, sett={sett_x}, exit={exit_x}, credits={cred_x}")
        
        # Update file
        update_file(play_x, sett_x, exit_x, cred_x)
    
    print("\n" + "=" * 60)
    print("DONE")
    print("=" * 60)

if __name__ == '__main__':
    main()
