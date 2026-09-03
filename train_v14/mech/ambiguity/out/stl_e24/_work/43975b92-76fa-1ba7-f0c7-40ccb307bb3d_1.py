from build123d import *

outer_width = 80.0
outer_depth = 60.0
outer_height = 30.0
wall_thickness = 5.0
inner_width = outer_width - 2 * wall_thickness
inner_depth = outer_depth - 2 * wall_thickness
cutout_width = 30.0
cutout_depth = 20.0
hole_diameter = 4.0
hole_rows = 3
hole_cols = 4
hole_spacing_x = 15.0
hole_spacing_y = 10.0
chamfer_size = 1.0

solid_body = Box(outer_width, outer_depth, outer_height) - Box(inner_width, inner_depth, outer_height)
solid_body = solid_body - Box(cutout_width, cutout_depth, outer_height)

for i in range(hole_cols):
    for j in range(hole_rows):
        x = (i - (hole_cols - 1) / 2) * hole_spacing_x
        z = (j - (hole_rows - 1) / 2) * hole_spacing_y
        solid_body = solid_body - Pos(x, outer_depth / 2, z) * Rot(90, 0, 0) * Cylinder(hole_diameter / 2, outer_depth + 10)

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = chamfer(top_face.edges(), chamfer_size)

part = solid_body
part.name = "hollow_frame_with_cutout_and_holes"
export_step(part, "output.step")