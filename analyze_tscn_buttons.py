#!/usr/bin/env python3
"""Analyze button dimensions from main.tscn"""

buttons = {
    'play': {
        'offset_left': -985.0,
        'offset_top': 304.0,
        'offset_right': 623.0,
        'offset_bottom': 1512.0,
        'scale': (0.297468, 0.311179)
    },
    'settings': {
        'offset_left': -551.0,
        'offset_top': 305.0,
        'offset_right': 1457.0,
        'offset_bottom': 1515.58,
        'scale': (0.309, 0.309)
    },
    'exit': {
        'offset_left': -35.0,
        'offset_top': 206.0,
        'offset_right': 108.0,
        'offset_bottom': 274.0,
        'scale': (6.722, 6.048)
    }
}

camera_zoom = (0.6, 0.545)

print('TSCN BUTTON DIMENSIONS ANALYSIS')
print('='*80)
print()

for name, btn in buttons.items():
    width = btn['offset_right'] - btn['offset_left']
    height = btn['offset_bottom'] - btn['offset_top']
    
    scaled_width = width * btn['scale'][0]
    scaled_height = height * btn['scale'][1]
    
    final_width = scaled_width * camera_zoom[0]
    final_height = scaled_height * camera_zoom[1]
    
    print(f'{name.upper()} BUTTON:')
    print(f'  Base size: {width:.1f} x {height:.1f}')
    print(f'  Scale factors: {btn["scale"][0]:.3f} x {btn["scale"][1]:.3f}')
    print(f'  After scale: {scaled_width:.1f} x {scaled_height:.1f}')
    print(f'  Camera zoom (0.6 x 0.545): {final_width:.1f} x {final_height:.1f}')
    print()

print('='*80)
print('COMPARISON WITH CURRENT PYGAME BUTTONS:')
print('='*80)
current_buttons = {
    'play': (140, 100),
    'settings': (140, 100),
    'exit': (120, 100)
}

print()
for name in ['play', 'settings', 'exit']:
    if name in buttons and name in current_buttons:
        btn = buttons[name]
        width = btn['offset_right'] - btn['offset_left']
        height = btn['offset_bottom'] - btn['offset_top']
        
        final_width = width * btn['scale'][0] * camera_zoom[0]
        final_height = height * btn['scale'][1] * camera_zoom[1]
        
        current = current_buttons[name]
        
        print(f'{name.upper()}:')
        print(f'  TSCN (with camera): {final_width:.1f} x {final_height:.1f}')
        print(f'  Current pygame: {current[0]} x {current[1]}')
        print(f'  Difference: {final_width - current[0]:.1f} x {final_height - current[1]:.1f}')
        print(f'  Scale ratio: {final_width / current[0]:.2f}x width, {final_height / current[1]:.2f}x height')
        print()
