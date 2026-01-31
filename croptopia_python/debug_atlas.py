#!/usr/bin/env python3
"""Debug script to analyze atlas coordinate patterns in spawn_node.tscn"""

import re
from collections import Counter

tscn_path = r"c:\Users\Jonas\Documents\doubOS\DoubOS\Croptopia - 02.11.25\scenes\spawn_node.tscn"

with open(tscn_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Find all tile_data sections
tile_data_matches = re.finditer(r'layer_\d+/tile_data = PackedInt32Array\((.*?)\)', content)

atlas_values = Counter()
source_ids = Counter()
combinations = Counter()

for match in tile_data_matches:
    data_str = match.group(1)
    numbers = [int(n.strip()) for n in data_str.split(',') if n.strip()]
    
    # Process triplets
    for i in range(0, len(numbers)-2, 3):
        pos = numbers[i]
        atlas_val = numbers[i+1]
        source = numbers[i+2]
        
        atlas_values[atlas_val] += 1
        source_ids[source] += 1
        combinations[(source, atlas_val)] += 1

print("Most common ATLAS values (value2):")
for atlas_val, count in atlas_values.most_common(20):
    atlas_x = atlas_val & 0xFFFF
    atlas_y = (atlas_val >> 16) & 0xFFFF
    print(f"  {atlas_val}: {atlas_x}x{atlas_y} (count: {count})")

print("\nSource IDs:")
for src_id, count in sorted(source_ids.items()):
    print(f"  {src_id}: {count} tiles")

print("\nMost common (source_id, atlas_value) pairs:")
for (src, atlas), count in combinations.most_common(15):
    atlas_x = atlas & 0xFFFF
    atlas_y = (atlas >> 16) & 0xFFFF
    print(f"  src={src}, atlas={atlas} ({atlas_x},{atlas_y}): {count} tiles")
