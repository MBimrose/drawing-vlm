from build123d import *

leaf_length = 80.0
leaf_width = 30.0
leaf_thickness = 6.0
notch_width = 6.0
notch_depth = 8.0
notch_offset = 12.0
slot_width = 4.0
slot_length = 20.0
slot_offset = 5.0
hole_diameter = 4.0
hole_spacing_x = 20.0
hole_spacing_y = 10.0
hole_rows = 2
hole_cols = 4
chamfer_size = 0.5
rib_width = 8.0
rib_height = 4.0
rib_thickness = 2.0

result = Box(leaf_length, leaf_width, leaf_thickness)

notch_x = -leaf_length/2 + notch_offset + notch_width/2
result = result - Pos(notch_x, 0, 0) * Box(notch_width, notch_depth, leaf_thickness)

slot_x = leaf_length/2 - leaf_thickness/4
result = result - Pos(slot_x, 0, 0) * Box(leaf_thickness/2, slot_length, slot_width)

rib_z = -leaf_thickness/2 + rib_thickness/2
result = result + Pos(0, 0, rib_z) * Box(rib_width, rib_height, rib_thickness)

for i in range(hole_cols):
    for j in range(hole_rows):
        x = (i - (hole_cols-1)/2) * hole_spacing_x
        y = (j - (hole_rows-1)/2) * hole_spacing_y
        result = result - Pos(x, y, 0) * Cylinder(hole_diameter/2, leaf_thickness)

result = chamfer(result.edges().filter_by(Axis.Z), chamfer_size)

part = result
part.name = "leaf_with_notch_slot_rib_holes"
export_step(part, "output.step")