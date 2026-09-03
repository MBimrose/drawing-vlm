from build123d import *

base_length = 80.0
base_width = 60.0
base_thickness = 6.0
frame_height = 8.0
frame_thickness = 5.0
rib_width = 10.0
rib_height = 4.0
hole_diameter = 4.0
hole_spacing_x = 18.0
hole_spacing_y = 18.0
hole_rows = 2
hole_cols = 4

base = Pos(0, 0, base_thickness/2) * Box(base_length, base_width, base_thickness)
frame_outer = Pos(0, 0, base_thickness + frame_height/2) * Box(base_length, base_width, frame_height)
frame_inner = Pos(0, 0, base_thickness + frame_height/2) * Box(base_length - 2*frame_thickness, base_width - 2*frame_thickness, frame_height)
frame = frame_outer - frame_inner
rib = Pos(0, 0, base_thickness + rib_height/2) * Box(base_length - 2*frame_thickness, rib_width, rib_height)
combined = base + frame + rib

hole_r = hole_diameter / 2
hole_h = base_thickness + frame_height + 10
hole_z = base_thickness + frame_height / 2
start_x = -((hole_cols - 1) * hole_spacing_x) / 2
start_y = -((hole_rows - 1) * hole_spacing_y) / 2
for i in range(hole_cols):
    for j in range(hole_rows):
        x = start_x + i * hole_spacing_x
        y = start_y + j * hole_spacing_y
        combined = combined - Pos(x, y, hole_z) * Cylinder(hole_r, hole_h)

part = combined
part.name = "base_plate_with_frame"
export_step(part, "output.step")