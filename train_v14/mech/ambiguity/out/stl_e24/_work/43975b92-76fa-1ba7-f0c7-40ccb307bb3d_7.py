from build123d import *

outer_length = 80.0
outer_width = 60.0
outer_height = 30.0
wall_thickness = 5.0
pocket_length = 40.0
pocket_width = 30.0
pocket_depth = 5.0
vent_hole_diameter = 4.0
vent_rows = 3
vent_cols = 4
vent_spacing_x = 15.0
vent_spacing_y = 10.0
chamfer_size = 1.0

inner_length = outer_length - 2 * wall_thickness
inner_width = outer_width - 2 * wall_thickness

solid_body = Box(outer_length, outer_width, outer_height)
solid_body = solid_body - Box(inner_length, inner_width, outer_height)
solid_body = solid_body - Pos(0, 0, outer_height - pocket_depth/2) * Box(pocket_length, pocket_width, pocket_depth)

for i in range(vent_cols):
    for j in range(vent_rows):
        x = (i - (vent_cols - 1) / 2) * vent_spacing_x
        z = (j - (vent_rows - 1) / 2) * vent_spacing_y
        solid_body = solid_body - Pos(x, outer_width/2, z) * Rot(90, 0, 0) * Cylinder(vent_hole_diameter/2, outer_height)

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = chamfer(top_face.edges(), chamfer_size)

part = solid_body
part.name = "ventilated_box"
export_step(part, "output.step")