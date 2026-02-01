import re
from pathlib import Path
import numpy as np
from PIL import Image

main_tscn = Path(r"Croptopia - 02.11.25/scenes/main.tscn").read_text(encoding="utf-8")

# Parse button nodes
buttons = {}
pattern = re.compile(r"\[node name=\"(?P<name>play|setting|exit)\" type=\"Button\" parent=\"\.\"\]\n(?P<body>.*?)(?=\n\[node|\Z)", re.S)
for m in pattern.finditer(main_tscn):
    name = m.group("name")
    body = m.group("body")

    def get_val(key, default=None):
        mm = re.search(r"%s = ([^\n]+)" % re.escape(key), body)
        if not mm:
            return default
        return mm.group(1).strip()

    offsets = {
        "left": float(get_val("offset_left", "0")),
        "top": float(get_val("offset_top", "0")),
        "right": float(get_val("offset_right", "0")),
        "bottom": float(get_val("offset_bottom", "0")),
    }

    scale = get_val("scale", None)
    if scale:
        sx, sy = scale.replace("Vector2(", "").replace(")", "").split(",")
        scale = (float(sx), float(sy))
    else:
        scale = (1.0, 1.0)

    buttons[name] = {"offsets": offsets, "scale": scale}

print("Buttons from main.tscn:")
for k, v in buttons.items():
    print(k, v)

# Compute Godot-space centers for each button
centers_godot = {}
for name, data in buttons.items():
    left = data["offsets"]["left"]
    top = data["offsets"]["top"]
    width = (data["offsets"]["right"] - data["offsets"]["left"]) * data["scale"][0]
    height = (data["offsets"]["bottom"] - data["offsets"]["top"]) * data["scale"][1]
    cx = left + width / 2.0
    cy = top + height / 2.0
    centers_godot[name] = (cx, cy)

print("\nGodot centers (raw):")
for k, v in centers_godot.items():
    print(k, v)

# Compute reference centers from image (within game window)
ref = Image.open("reference_do_not_modify.png").convert("RGB")
ref_arr = np.array(ref)

# Game window bounds (purple region)
r, g, b = ref_arr[:, :, 0], ref_arr[:, :, 1], ref_arr[:, :, 2]
purple = (r == 121) & (g == 78) & (b == 237)
y_p, x_p = np.where(purple)
if len(x_p) == 0:
    raise SystemExit("No purple region found")
left_w, right_w = int(np.min(x_p)), int(np.max(x_p))
top_w, bottom_w = int(np.min(y_p)), int(np.max(y_p))

# Extract game window
window = ref_arr[top_w : bottom_w + 1, left_w : right_w + 1, :]
wh, ww = window.shape[0], window.shape[1]

# Button color mask in reference
r_w, g_w, b_w = window[:, :, 0], window[:, :, 1], window[:, :, 2]
btn_mask = (r_w > 200) & (g_w > 150) & (g_w < 240) & (b_w < 150)

# Split into thirds for left/mid/right
third = ww // 3
masks = {
    "play": btn_mask[:, :third],
    "setting": btn_mask[:, third : 2 * third],
    "exit": btn_mask[:, 2 * third :],
}
centers_ref = {}
for name, mask in masks.items():
    y, x = np.where(mask)
    if len(x) == 0:
        centers_ref[name] = None
        continue
    # adjust x offset for mid/right
    x_offset = 0
    if name == "setting":
        x_offset = third
    elif name == "exit":
        x_offset = 2 * third
    cx = np.mean(x) + x_offset
    cy = np.mean(y)
    centers_ref[name] = (cx, cy)

print("\nReference window bounds:", (left_w, top_w, right_w, bottom_w), "size", (ww, wh))
print("Reference centers (window coords):")
for k, v in centers_ref.items():
    print(k, v)

# Solve affine (scale + offset) mapping from godot centers to reference window centers
# x_ref = ax * x_godot + bx
# y_ref = ay * y_godot + by

godot_pts = []
ref_pts = []
for name in ["play", "setting", "exit"]:
    if centers_ref[name] is None:
        continue
    godot_pts.append(centers_godot[name])
    ref_pts.append(centers_ref[name])

godot_pts = np.array(godot_pts)
ref_pts = np.array(ref_pts)

# Solve ax,bx
A = np.column_stack([godot_pts[:, 0], np.ones(len(godot_pts))])
ax, bx = np.linalg.lstsq(A, ref_pts[:, 0], rcond=None)[0]
A = np.column_stack([godot_pts[:, 1], np.ones(len(godot_pts))])
ay, by = np.linalg.lstsq(A, ref_pts[:, 1], rcond=None)[0]

print("\nMapping:")
print("x_ref = %.6f * x_godot + %.6f" % (ax, bx))
print("y_ref = %.6f * y_godot + %.6f" % (ay, by))

# Compute target centers in reference window using mapping
mapped_centers = {}
for name, (cx, cy) in centers_godot.items():
    rx = ax * cx + bx
    ry = ay * cy + by
    mapped_centers[name] = (rx, ry)

print("\nMapped centers to reference window:")
for k, v in mapped_centers.items():
    print(k, v)

# Convert reference window coords to pygame (1152x648)
scale_x = 1152 / ww
scale_y = 648 / wh

print("\nScale to pygame:", scale_x, scale_y)

mapped_centers_py = {k: (v[0] * scale_x, v[1] * scale_y) for k, v in mapped_centers.items()}
print("\nMapped centers to pygame:")
for k, v in mapped_centers_py.items():
    print(k, v)

# Sprite sizes
sizes = {
    "play": (287, 205),
    "setting": (372, 204),
    "exit": (577, 224),
}

# Compute top-left positions
positions = {}
for k, (cx, cy) in mapped_centers_py.items():
    w, h = sizes[k]
    positions[k] = (int(round(cx - w / 2)), int(round(cy - h / 2)))

print("\nSuggested pygame top-left positions:")
for k, v in positions.items():
    print(k, v)
