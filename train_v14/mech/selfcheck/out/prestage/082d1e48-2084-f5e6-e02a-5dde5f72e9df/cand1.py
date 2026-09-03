from build123d import *

outer_length = 80.0
outer_width = 50.0
outer_height = 30.0
wall_thickness = 5.0
inner_length = 50.0
inner_width = 30.0
inner_depth = 24.0
fillet_radius = 2.0
hole_diameter = 8.0
hole_offset_x = 15.0
hole_offset_y = 15.0

solid_body = Pos(0, 0, outer_height/2) * Box(outer_length, outer_width, outer_height)
solid_body = fillet(solid_body.edges().filter_by(Axis.Z), fillet_radius)
inner_cut = Pos(0, 0, outer_height - inner_depth/2) * Box(inner_length, inner_width, inner_depth)
solid_body = solid_body - inner_cut
hole = Pos(outer_length/2 - hole_offset_x, 0, outer_height/2) * Rot(0, 90, 0) * Cylinder(hole_diameter/2, outer_length)
solid_body = solid_body - hole

part = solid_body
part.name = "box_with_cavity_and_hole"
export_step(part, "output.step")