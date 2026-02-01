#!/usr/bin/env python3
# Calculate button X positions to match reference span

# Button widths from TSCN
play_w = 287
settings_w = 372
exit_w = 577

# Reference span in 800x600: X=36 to X=614 (total 578px)
ref_start = 36
ref_end = 614
ref_span = ref_end - ref_start  # 578

total_button_width = play_w + settings_w + exit_w  # 1236

# Since buttons are 1236px but span is only 578px, they must overlap significantly
# Let's calculate required overlap
required_compression = total_button_width - ref_span  # 658px to compress
# 2 gaps, so ~329px overlap per gap

overlap = required_compression / 2

print("Button Layout Calculation:")
print("="*60)
print(f"Button widths: play={play_w}, settings={settings_w}, exit={exit_w}")
print(f"Total width if no overlap: {total_button_width}")
print(f"Reference span: {ref_span} (from {ref_start} to {ref_end})")
print(f"Required compression: {required_compression}")
print(f"Overlap per gap: {overlap:.0f}")
print()

# Position buttons
play_x = ref_start
settings_x = play_x + play_w - overlap
exit_x = settings_x + settings_w - overlap

print("Calculated Positions:")
print(f"  play: X={play_x:.0f}")
print(f"  settings: X={settings_x:.0f}")
print(f"  exit: X={exit_x:.0f}")
print(f"  Total span: {exit_x + exit_w:.0f} (should be ~{ref_end})")
print()

# For Y: reference Y=478-593, midpoint = 535
# Current Y=425, probably too high
ref_y_mid = (478 + 593) / 2
print(f"Reference Y midpoint: {ref_y_mid}")
print(f"Suggested Y (for 205px tall button): {ref_y_mid - 205/2:.0f}")
