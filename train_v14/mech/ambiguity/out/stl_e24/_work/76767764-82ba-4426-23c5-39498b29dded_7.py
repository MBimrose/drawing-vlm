from build123d import *

leaf_length = 80
leaf_width = 30
leaf_thickness = 6
groove_width = 12
groove_depth = 2
groove_length = leaf_length - 20
hole_diameter = 4
hole_spacing_x = 20
hole_spacing_y = 10
hole_rows = 2
hole_cols = 4
chamfer_size = 0.5
notch_width = 6
notch_height = 8
notch_offset = 15

solid_body = Box(leaf_length, leaf_width, leaf_thickness)

notch_x = -leaf_length/2 + notch_offset
solid_body = solid_body - Pos(notch_x, 0, 0) * Box(notch_width, notch_height, leaf_thickness)

notch_edges = solid_body.edges().filter_by(Axis.Z).sort_by(Axis.X)[2:6]
solid_body = chamfer(notch_edges, chamfer_size)

groove_x = leaf_length/2 - groove_depth/2
solid_body = solid_body - Pos(groove_x, 0, 0) * Box(groove_depth, groove_width, groove_length)

for i in range(hole_cols):
    for j in range(hole_rows):
        hx = -leaf_length/2 + hole_spacing_x/2 + i*hole_spacing_x
        hy = -leaf_width/2 + hole_spacing_y/2 + j*hole_spacing_y
        solid_body = solid_body - Pos(hx, hy, 0) * Cylinder(hole_diameter/2, leaf_thickness)

part = solid_body
part.name = "leaf_with_notch_groove_holes"
export_step(part, "output.step")