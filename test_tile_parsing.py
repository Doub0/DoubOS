#!/usr/bin/env python3
"""Test script to verify corrected tile parsing"""

import sys
sys.path.insert(0, 'croptopia_python')

from croptopia.godot_parser import GodotTSCNParser

print("Starting parser...")
parser = GodotTSCNParser('Croptopia - 02.11.25/scenes/spawn_node.tscn', 'Croptopia - 02.11.25/assets')
print("Parsing...")
data = parser.parse()
print(f"Parse result: {data is not None}")

if not data:
    print("Failed to parse data")
    sys.exit(1)

print(f"Layers found: {list(data.get('layers', {}).keys())}")
print(f"Tileset sources: {len(data.get('tileset_sources', {}))}")

# Check layer 6 (grass - has 3342 tiles)
layer_idx = 6
layer_data = data['layers'].get(layer_idx, {})
tiles = layer_data.get('tiles', [])

print(f"\nLayer {layer_idx}: {layer_data.get('name')}")
print(f"Total tiles: {len(tiles)}")

if not tiles:
    print("No tiles in layer 6")
    sys.exit(1)

# Check tuple format
print(f"First tile format (tuple length): {len(tiles[0])}")
print(f"First 3 tiles: {tiles[:3]}")

# Check bounds
errors = 0
for i, tile in enumerate(tiles):
    if len(tile) != 6:
        print(f"ERROR: tile {i} has {len(tile)} values, expected 6: {tile}")
        continue
        
    x, y, source_id, atlas_x, atlas_y, alt_id = tile
    
    if source_id not in data['tileset_sources']:
        if errors < 5:
            print(f"  ERROR: source_id {source_id} not in tileset sources")
        errors += 1
        continue
        
    src_def = data['tileset_sources'][source_id]
    max_x, max_y = src_def.get('atlas_max', (0, 0))
    
    if atlas_x < 0 or atlas_x >= max_x or atlas_y < 0 or atlas_y >= max_y:
        if errors < 5:
            print(f"  ERROR: pos({x},{y}) src={source_id} atlas({atlas_x},{atlas_y}) outside 0-{max_x-1}x0-{max_y-1}")
        errors += 1

if errors == 0:
    print(f"✓ All {len(tiles)} tiles have valid bounds!")
else:
    print(f"✗ Found {errors} errors out of {len(tiles)} tiles")
