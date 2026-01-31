#!/usr/bin/env python3
"""Check tileset source dimensions"""

import sys
sys.path.insert(0, 'croptopia_python')

from croptopia.godot_parser import GodotTSCNParser

parser = GodotTSCNParser('Croptopia - 02.11.25/scenes/spawn_node.tscn', 'Croptopia - 02.11.25/assets')
data = parser.parse()

if not data:
    print("Failed to parse")
    sys.exit(1)

print("Tileset source dimensions:")
for src_id in sorted(data['tileset_sources'].keys())[:20]:
    src = data['tileset_sources'][src_id]
    max_x, max_y = src.get('atlas_max', (0, 0))
    print(f"  Source {src_id}: {max_x}x{max_y}")
    
print()
print(f"Source 3: {data['tileset_sources'][3].get('atlas_max')}")
print(f"Source 2: {data['tileset_sources'][2].get('atlas_max')}")
print(f"Source 4: {data['tileset_sources'][4].get('atlas_max')}")
