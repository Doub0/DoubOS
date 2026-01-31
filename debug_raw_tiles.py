#!/usr/bin/env python3
"""Debug raw tile data before decoding"""

import re
from pathlib import Path

tscn_path = 'Croptopia - 02.11.25/scenes/spawn_node.tscn'

print(f"Reading {tscn_path}...")
with open(tscn_path, 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()

# Find layer 6 data
tilemap_pattern = r'\[node name="TileMap2".*?\n(.*?)\n\[node'
tilemap_match = re.search(tilemap_pattern, content, re.DOTALL)

if not tilemap_match:
    print("TileMap2 not found")
    exit(1)

tilemap_content = tilemap_match.group(1)

# Find layer 6 data
tile_match = re.search(r'layer_6/tile_data = PackedInt32Array\(([^)]*)\)', tilemap_content)

if not tile_match:
    print("Layer 6 tile data not found - trying to list what's there...")
    # List what layers we have
    layer_pattern = r'layer_(\d+)/tile_data'
    matches = re.findall(layer_pattern, tilemap_content)
    print(f"Layers with tile_data: {sorted(set(matches))}")
    exit(1)

tile_data_str = tile_match.group(1)
numbers = [int(n.strip()) for n in tile_data_str.split(',') if n.strip()]

print(f"Total numbers in PackedInt32Array: {len(numbers)}")
print(f"Number of tile triplets: {len(numbers) // 3}")
print()

# Show first 15 numbers (5 tiles worth)
print("First 5 tiles in raw format:")
for i in range(0, min(15, len(numbers)), 3):
    val1, val2, val3 = numbers[i], numbers[i+1], numbers[i+2]
    print(f"  Tile {i//3}: pos={val1}, val2={val2}, val3={val3}")
    
    # Decode value2
    if val2 < 0:
        val2_unsigned = val2 + (1 << 32)
    else:
        val2_unsigned = val2
    atlas_x_from_val2 = val2_unsigned & 0xFFFF
    source_id_from_val2 = (val2_unsigned >> 16) & 0xFFFF
    
    # Decode value3
    if val3 < 0:
        val3_unsigned = val3 + (1 << 32)
    else:
        val3_unsigned = val3
    atlas_y_from_val3 = val3_unsigned & 0xFFFF
    alt_id_from_val3 = (val3_unsigned >> 16) & 0xFFFF
    
    print(f"         → atlas_x={atlas_x_from_val2}, source_id={source_id_from_val2}, atlas_y={atlas_y_from_val3}, alt_id={alt_id_from_val3}")
