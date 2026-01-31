# TSCN Button Position Analysis

## CRITICAL FINDINGS

### Button Coordinate System
Godot Control nodes use `offset_left/top/right/bottom` format:
- These are raw pixel coordinates relative to parent node
- `scale` property applies AFTER offset calculation
- Final rect = (offset values × scale)

### EXACT BUTTON DATA FROM main.tscn

#### PLAY Button
```
Raw offsets: left=-985, top=304, right=623, bottom=1512
Unscaled rect: (-985, 304, 623, 1512)
Unscaled width: 1608px
Unscaled height: 1208px
Scale: 0.297468 × 0.311179
SCALED SIZE: 478px × 376px
SCALED POSITION: (-292.6, 94.6)
```

#### SETTINGS Button
```
Raw offsets: left=-551, top=305, right=1457, bottom=1515.58
Unscaled rect: (-551, 305, 1457, 1515.58)
Unscaled width: 2008px
Unscaled height: 1210.58px
Scale: 0.309 × 0.309
SCALED SIZE: 620px × 374px
SCALED POSITION: (-170.3, 94.2)
```

#### EXIT Button
```
Raw offsets: left=-35, top=206, right=108, bottom=274
Unscaled rect: (-35, 206, 108, 274)
Unscaled width: 143px
Unscaled height: 68px
Scale: 6.722 × 6.048
SCALED SIZE: 961px × 411px
SCALED POSITION: (-235.3, 1247.1)
```

#### CREDITS Button (Label)
```
Raw offsets: left=506, top=459, right=514, bottom=485
Unscaled rect: (506, 459, 514, 485)
Unscaled width: 8px
Unscaled height: 26px
Scale: 3.20291 × 5.30584
SCALED SIZE: 25.6px × 137.95px
SCALED POSITION: (1620.3, 2432.7)
```

### Camera Information
- Camera2D position: (13, -2)
- Camera zoom: (0.6, 0.545)
- Effective viewport center: ~(13, -2)

### Key Insight
All these buttons are positioned in GLOBAL SPACE with the camera offset at (13, -2).
To convert to pygame/screen space (0,0 at top-left), we need to:
1. Take Godot coordinates relative to camera
2. Apply camera offset
3. Apply camera zoom
4. Map to pygame display (800×600)

## SPLASH ANIMATION

### TextureRect Asset
```
ExtResource ID: "8_8bf4v"
File: pixil-frame-0 - 2024-02-26T083114.993.png
Position: top_level=true
Offset: left=-1655, top=435, right=-1615, bottom=475
Unscaled size: 40×40px
Rotation: 3.14159 (180 degrees)
Scale: 24.535 × 24.535
SCALED SIZE: ~980px × 980px
```

### Animation Tracks
**Phase 1 (0s to 2s):**
- TextureRect self_modulate alpha: 0 → 1 (fades IN)
- TextureRect modulate color: stays at (0.470588, 0, 0.207843, 0) → then animated
- ColorRect visibility: 1
- ColorRect2 visibility: 2

**Phase 2 (2s to 2.5s):**
- TextureRect self_modulate alpha: 1 → 0 (fades OUT)
- ColorRect visibility: 1
- ColorRect2 visibility: 2

### ColorRects
- ColorRect: Gray (0.164706, 0.164706, 0.164706, 1)
- ColorRect2: Same gray color, position animates
