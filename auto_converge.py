#!/usr/bin/env python3
"""Automatically converge button positions"""

import os
import subprocess
import time
from PIL import Image
import numpy as np

def measure():
    cur = Image.open('screenshot_menu_surface.png')
    ref = Image.open('reference_menu.png')
    cur_arr = np.array(cur)
    ref_arr = np.array(ref)[:, :, :3]
    
    co = (cur_arr[:,:,0]>170) & (cur_arr[:,:,1]>70) & (cur_arr[:,:,1]<150) & (cur_arr[:,:,2]<90)
    ro = (ref_arr[:,:,0]>170) & (ref_arr[:,:,1]>70) & (ref_arr[:,:,1]<150) & (ref_arr[:,:,2]<90)
    
    cy, cx = np.where(co)
    ry, rx = np.where(ro)
    
    cc = (np.mean(cx), np.mean(cy))
    rc = (np.mean(rx) / (ref_arr.shape[1]/800), np.mean(ry) / (ref_arr.shape[0]/600))
    
    o = (rc[0] - cc[0], rc[1] - cc[1])
    mag = (o[0]**2 + o[1]**2)**0.5
    return o, mag

def update_file(play, sett, exit_x, cred, play_y, sett_y, exit_y, cred_y):
    code = open('croptopia_python/croptopia/scenes/main_menu_scene.py', 'r').read()
    
    # Find and replace the button rect lines
    import re
    
    code = re.sub(
        r"'play': \{[^}]*'rect': pygame\.Rect\([^)]+\)",
        f"'play': {{\n                'rect': pygame.Rect({play}, {play_y}, 140, 100)",
        code, count=1, flags=re.DOTALL
    )
    # Actually this is too complex. Let me just do string replace more carefully
    
    # Read file and replace each button line
    lines = code.split('\n')
    for i, line in enumerate(lines):
        if "'play':" in line and i < len(lines) - 2:
            # Next line should have the rect
            if 'pygame.Rect' in lines[i+2]:
                lines[i+2] = f"                'rect': pygame.Rect({play}, {play_y}, 140, 100),"
        elif "'settings':" in line and i < len(lines) - 2:
            if 'pygame.Rect' in lines[i+2]:
                lines[i+2] = f"                'rect': pygame.Rect({sett}, {sett_y}, 140, 100),"
        elif "'exit':" in line and i < len(lines) - 2:
            if 'pygame.Rect' in lines[i+2]:
                lines[i+2] = f"                'rect': pygame.Rect({exit_x}, {exit_y}, 120, 100),"
        elif "'credits':" in line and i < len(lines) - 2:
            if 'pygame.Rect' in lines[i+2]:
                lines[i+2] = f"                'rect': pygame.Rect({cred}, {cred_y}, 200, 30),"
    
    code = '\n'.join(lines)
    open('croptopia_python/croptopia/scenes/main_menu_scene.py', 'w').write(code)

# Current positions (from last measurement)
pos = {'play': 0, 'sett': 115, 'exit': 265, 'cred': 395}
y_pos = {'play': 437, 'sett': 437, 'exit': 437, 'cred': 487}

print("=" * 60)
print("AUTO-CONVERGE BUTTON POSITIONS")
print("=" * 60)

for it in range(1, 8):
    # Run game
    if os.path.exists('screenshot_menu_surface.png'):
        os.remove('screenshot_menu_surface.png')
    
    print(f"\n[Iteration {it}]")
    print(f"Positions: play={pos['play']}, sett={pos['sett']}, exit={pos['exit']}, cred={pos['cred']}")
    
    proc = subprocess.Popen(['python', 'croptopia_python/main.py'], 
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(7)
    try:
        proc.terminate()
        proc.wait(timeout=2)
    except:
        proc.kill()
    
    # Measure
    o, mag = measure()
    print(f"Offset: ({o[0]:.1f}, {o[1]:.1f}) | Magnitude: {mag:.2f}px")
    
    if mag < 0.5:
        print("\n✓ CONVERGED! Buttons are pixel-perfect.")
        break
    
    # Apply offset (half-step for stability)
    step = 0.8  # Use 80% of offset to avoid oscillation
    pos['play'] = max(0, int(round(pos['play'] + o[0] * step)))
    pos['sett'] = max(0, int(round(pos['sett'] + o[0] * step)))
    pos['exit'] = max(0, int(round(pos['exit'] + o[0] * step)))
    pos['cred'] = max(0, int(round(pos['cred'] + o[0] * step)))
    
    y_pos['play'] = int(round(y_pos['play'] + o[1] * step))
    y_pos['sett'] = int(round(y_pos['sett'] + o[1] * step))
    y_pos['exit'] = int(round(y_pos['exit'] + o[1] * step))
    y_pos['cred'] = int(round(y_pos['cred'] + o[1] * step))
    
    # Update file
    update_file(pos['play'], pos['sett'], pos['exit'], pos['cred'],
               y_pos['play'], y_pos['sett'], y_pos['exit'], y_pos['cred'])

print("\n" + "=" * 60)
print("COMPLETE!")
print("=" * 60)
