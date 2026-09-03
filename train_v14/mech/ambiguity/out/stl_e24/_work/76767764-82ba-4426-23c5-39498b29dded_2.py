from build123d import *

leaf_length = 80
leaf_width = 30
leaf_thickness = 6
pin_hole_diameter = 4
pin_spacing_x = 20
pin_spacing_y = 10
pin_rows = 2
pin_cols = 4
slot_width = 5
slot_length = 20
slot_depth = leaf_thickness / 2
rib_width = 6
rib_height = 8
rib_offset = 15

result = Box(leaf_length, leaf_width, leaf_thickness)

for i in range(pin_cols):
    for j in range(pin_rows):
        x = (i - (pin_cols - 1) / 2) * pin_spacing_x
        y = (j - (pin_rows - 1) / 2) * pin_spacing_y
        result = result - Pos(x, y, 0) * Cylinder(pin_hole_diameter / 2, leaf_thickness)

slot = Pos(leaf_length / 2 - slot_depth / 2, 0, 0) * Box(slot_depth, slot_length, slot_width)
result = result - slot

rib = Pos(-leaf_length / 2 + rib_offset, 0, 0) * Box(rib_width, rib_height, leaf_thickness)
result = result - rib

part = result
part.name = "leaf_plate"
export_step(part, "output.step")