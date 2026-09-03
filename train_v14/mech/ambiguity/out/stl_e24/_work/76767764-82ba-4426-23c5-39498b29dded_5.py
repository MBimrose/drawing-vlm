from build123d import *

leaf_length = 80.0
leaf_width = 30.0
leaf_thickness = 6.0
notch_width = 8.0
notch_depth = 4.0
pocket_width = 20.0
pocket_height = 12.0
pocket_depth = 2.0
hole_diameter = 4.0
hole_rows = 2
hole_cols = 4
hole_spacing_x = 20.0
hole_spacing_y = 10.0

solid = Box(leaf_length, leaf_width, leaf_thickness)

notch_x = -leaf_length/2 + 15
solid = solid - Pos(notch_x, 0, 0) * Box(notch_width, leaf_thickness, leaf_thickness)

pocket_x = leaf_length/2 - pocket_depth/2
solid = solid - Pos(pocket_x, 0, 0) * Box(pocket_depth, pocket_width, pocket_height)

hole_x_start = -leaf_length/2 + hole_spacing_x/2
hole_y_start = -leaf_width/2 + hole_spacing_y/2
for i in range(hole_cols):
    for j in range(hole_rows):
        x = hole_x_start + i * hole_spacing_x
        y = hole_y_start + j * hole_spacing_y
        solid = solid - Pos(x, y, 0) * Cylinder(hole_diameter/2, leaf_thickness)

part = solid
part.name = "leaf_with_notch_pocket_holes"
export_step(part, "output.step")