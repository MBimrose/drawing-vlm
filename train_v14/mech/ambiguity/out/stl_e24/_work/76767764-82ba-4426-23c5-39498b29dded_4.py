from build123d import *

bracket_length = 80.0
bracket_width = 30.0
bracket_thickness = 6.0
slot_width = 6.0
slot_height = 12.0
slot_offset_from_left = 15.0
hole_diameter = 4.0
hole_spacing_x = 20.0
hole_spacing_y = 10.0
hole_rows = 2
hole_cols = 4
rib_width = 4.0
rib_height = 10.0
rib_spacing = 12.0

result = Box(bracket_length, bracket_width, bracket_thickness)

slot_center_x = -bracket_length/2 + slot_offset_from_left
result = result - Pos(slot_center_x, 0, 0) * Box(slot_width, slot_height, bracket_thickness)

hole_start_x = -bracket_length/2 + hole_spacing_x/2
hole_start_y = -bracket_width/2 + hole_spacing_y/2
for i in range(hole_cols):
    for j in range(hole_rows):
        hx = hole_start_x + i * hole_spacing_x
        hy = hole_start_y + j * hole_spacing_y
        result = result - Pos(hx, hy, 0) * Cylinder(hole_diameter/2, bracket_thickness)

rib_start_y = -bracket_width/2 + rib_spacing/2
rib_count = int(bracket_width // rib_spacing)
for k in range(rib_count):
    ry = rib_start_y + k * rib_spacing
    result = result - Pos(bracket_length/2 - bracket_thickness/4, ry, 0) * Box(bracket_thickness/2, rib_width, rib_height)

part = result
part.name = "bracket"
export_step(part, "output.step")