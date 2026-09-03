from build123d import *

length = 80.0
width = 30.0
thickness = 6.0
notch_width = 12.0
notch_depth = 4.0
hole_diameter = 4.0
hole_rows = 2
hole_cols = 4
hole_spacing_x = 20.0
hole_spacing_y = 10.0
rib_width = 6.0
rib_height = 8.0
rib_offset = 15.0

solid_body = Box(length, width, thickness)

left_notch = Pos(-length/2 + notch_depth/2, 0, 0) * Box(notch_depth, notch_width, thickness)
solid_body = solid_body - left_notch

right_notch = Pos(length/2 - notch_depth/2, 0, 0) * Box(notch_depth, notch_width, thickness)
solid_body = solid_body - right_notch

rib_cut = Pos(-length/2 + rib_offset, 0, 0) * Box(rib_width, rib_height, thickness)
solid_body = solid_body - rib_cut

for i in range(hole_cols):
    for j in range(hole_rows):
        x = (i - (hole_cols - 1) / 2) * hole_spacing_x
        y = (j - (hole_rows - 1) / 2) * hole_spacing_y
        solid_body = solid_body - Pos(x, y, 0) * Cylinder(hole_diameter/2, thickness)

part = solid_body
part.name = "notched_plate_with_holes"
export_step(part, "output.step")