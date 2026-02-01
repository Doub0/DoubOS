"""
Create a visualization showing button rect positions
"""
from PIL import Image, ImageDraw

# Create test surface showing button positions
width, height = 1152, 648
img = Image.new('RGB', (width, height), color=(121, 78, 237))  # Purple background
draw = ImageDraw.Draw(img)

# Current button positions
buttons = {
    'play': (27, -23, 287, 205),
    'settings': (-15, -23, 372, 204),
    'exit': (28, -23, 577, 224),
}

colors = {
    'play': (100, 200, 100),
    'settings': (200, 150, 100),
    'exit': (200, 100, 100),
}

print('Current button positions (rect x, y, w, h):')
for name, (x, y, w, h) in buttons.items():
    print(f'  {name}: ({x}, {y}, {w}, {h})')
    # Draw bounding box
    x1, y1 = x, y
    x2, y2 = x + w, y + h
    color = colors[name]
    draw.rectangle([x1, y1, x2, y2], outline=color, width=3)
    draw.text((x+5, max(5, y+5)), name, fill=color)

img.save('button_layout_current.png')
print('\nSaved: button_layout_current.png')
print('Issue: play, settings, exit buttons have Y=-23 (OFF SCREEN above)')
print('       They should have positive Y values inside 0-648 range')
