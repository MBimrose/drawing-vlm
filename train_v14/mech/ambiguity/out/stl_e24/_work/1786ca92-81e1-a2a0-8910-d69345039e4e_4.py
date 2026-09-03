from build123d import *

outer_diameter = 40.0
wall_thickness = 3.0
length = 80.0
groove_width = 12.0
groove_depth = 2.0
groove_position = 30.0
hole_diameter = 8.0
hole_position = 40.0
rib_width = 6.0
rib_height = 10.0
rib_thickness = 2.0
rib_position = 20.0

outer_radius = outer_diameter / 2.0
inner_radius = outer_radius - wall_thickness

solid_body = Cylinder(outer_radius, length)
top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face])

groove = Pos(0, 0, groove_position - length/2) * Box(groove_width, groove_depth, groove_depth)
solid_body = solid_body - groove

hole = Pos(0, 0, hole_position - length/2) * Rot(0, 90, 0) * Cylinder(hole_diameter/2, outer_diameter)
solid_body = solid_body - hole

rib = Pos(outer_radius + rib_thickness/2, 0, rib_position - length/2) * Box(rib_thickness, rib_width, rib_height)
solid_body = solid_body + rib

part = solid_body
part.name = "hollow_cylinder_with_groove_hole_rib"
export_step(part, "output.step")