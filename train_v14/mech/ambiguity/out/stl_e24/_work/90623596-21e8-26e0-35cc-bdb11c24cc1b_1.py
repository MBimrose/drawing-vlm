from build123d import *

outer_length = 80.0
outer_width = 50.0
outer_height = 30.0
wall_thickness = 2.0
groove_width = 6.0
groove_depth = 4.0
groove_length = outer_length - 2 * wall_thickness - 10.0
set_screw_diameter = 4.0
set_screw_depth = 8.0
chamfer_size = 0.5

solid_body = Pos(0, 0, outer_height/2) * Box(outer_length, outer_width, outer_height)
top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face])

groove = Pos(0, 0, outer_height - groove_depth/2) * Box(groove_length, groove_width, groove_depth)
solid_body = solid_body - groove

hole = Pos(outer_length/2 - set_screw_depth/2, 0, outer_height/2) * Rot(0, 90, 0) * Cylinder(set_screw_diameter/2, set_screw_depth)
solid_body = solid_body - hole

solid_body = chamfer(solid_body.edges(), chamfer_size)

part = solid_body
part.name = "shelled_box_with_groove_and_hole"
export_step(part, "output.step")