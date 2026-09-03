from build123d import *

outer_width = 80.0
outer_depth = 50.0
outer_height = 30.0
wall_thickness = 6.0
inner_width = 50.0
inner_depth = 30.0
inner_height = outer_height - wall_thickness
fillet_radius = 2.0
hole_diameter = 8.0
hole_offset_y = 0.0
hole_offset_z = 0.0

outer = Pos(0, 0, outer_height/2) * Box(outer_width, outer_depth, outer_height)
inner = Pos(0, 0, wall_thickness + inner_height/2) * Box(inner_width, inner_depth, inner_height)
solid_body = outer - inner

solid_body = fillet(solid_body.edges().filter_by(Axis.Z), fillet_radius)

hole = Pos(outer_width/2, hole_offset_y, outer_height/2 + hole_offset_z) * Rot(0, 90, 0) * Cylinder(hole_diameter/2, outer_width)
solid_body = solid_body - hole

part = solid_body
part.name = "XMountSocket"
export_step(part, "output.step")