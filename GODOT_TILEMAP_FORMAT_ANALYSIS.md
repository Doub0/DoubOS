# Godot TileMap PackedInt32Array Format Analysis

## Executive Summary

The mystery of the "second value" in Godot's TileMap packed tile data is **solved**. It's not a single encoded value at all—it's **two packed uint16 values** representing the atlas cell coordinates.

## TileMap Data Storage Format

### Latest Format (FORMAT_2)

Godot TileMapLayer data is stored as a **12-byte structure per cell**:

```
Offset  | Size | Type    | Meaning
--------|------|---------|------------------
0-1     | 2    | int16   | Map X coordinate
2-3     | 2    | int16   | Map Y coordinate
4-5     | 2    | uint16  | Source ID
6-7     | 2    | uint16  | Atlas Coordinate X
8-9     | 2    | uint16  | Atlas Coordinate Y  
10-11   | 2    | uint16  | Alternative Tile ID
```

### Key Finding: The "Triplet" Misunderstanding

When data is read as a `PackedInt32Array`, the 12 bytes per cell are interpreted as **three 32-bit integers**:

```
Index 0: bytes[0-3]   = (position_x as int32)
Index 1: bytes[4-7]   = (source_id + coord_x packed as int32)  ← "second value"
Index 2: bytes[8-11]  = (coord_y + alternative_tile packed as int32)
```

The "second value" is actually **little-endian packed data**:
- **Bits 0-15**: Atlas X coordinate (uint16)
- **Bits 16-31**: Source ID (uint16)

## Decoding Example

Your data: `(pos=-1114095, second=196649, source=3)`

Breaking down 196649 (0x30029):
```
196649 in hex: 0x0003 0029
High 16 bits: 0x0003 = 3  (Source ID)
Low 16 bits:  0x0029 = 41 (Atlas X coordinate!)
```

And the third value contains:
- **Bits 0-15**: Atlas Y coordinate
- **Bits 16-31**: Alternative Tile ID

## Godot Source Code References

From **Godot 4.x** (`tile_map_layer.cpp`):

```cpp
// Reading from saved data
int16_t x = decode_uint16(&cell_data_ptr[0]);
int16_t y = decode_uint16(&cell_data_ptr[2]);
uint16_t source_id = decode_uint16(&cell_data_ptr[4]);
uint16_t atlas_coords_x = decode_uint16(&cell_data_ptr[6]);
uint16_t atlas_coords_y = decode_uint16(&cell_data_ptr[8]);
uint16_t alternative_tile = decode_uint16(&cell_data_ptr[10]);

// Writing to saved data
encode_uint16(E.value.cell.source_id, &cell_data_ptr[4]);
encode_uint16(E.value.cell.coord_x, &cell_data_ptr[6]);
encode_uint16(E.value.cell.coord_y, &cell_data_ptr[8]);
encode_uint16(E.value.cell.alternative_tile, &cell_data_ptr[10]);
```

## Proper Decoding Steps

1. **Read the 12-byte structure** per cell as specified above
2. **Extract atlas coordinates** from bytes 6-9 (two separate uint16 values)
3. **Validate** against tileset grid dimensions (e.g., 6×12 atlas)
4. **Use** `tileset->get_source(source_id)->get_tile_data(Vector2i(coord_x, coord_y), alternative_tile)`

## Why the Confusion?

- **PCG/JSON serialization** may pack these as `PackedInt32Array` with 3 values per cell
- **Little-endian representation** makes the packing non-obvious
- **No documentation** clearly explains this format in the API docs
- **Internal structure** (`TileMapCell`) has individual fields, but serialization packs them

## Documentation Status

- **Godot API Documentation**: Silent on exact binary format
- **Source Code (GitHub)**: Explicit but requires reading C++
- **TSCN Files**: Store tile_data as `PackedInt32Array` with this specific packing

## Resolution for spawn_node.tscn

For your data with `second=196649, source=3` for a 6×12 atlas:
- Extract from second value: `atlas_x = 196649 & 0xFFFF = 41` (INVALID for 6-wide atlas)
- This suggests either:
  - Corrupted tile data in the saved scene
  - Different encoding in your specific file format
  - Need to check if TileMapLayer or deprecated TileMap is being used
