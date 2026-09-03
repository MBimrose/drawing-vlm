from build123d import *

outer_diameter = 40.0
wall_thickness = 3.0
length = 80.0
groove_width = 10.0
groove_depth = 2.0
port_diameter = 8.0
rib_height = 12.0
rib_width = 6.0
rib_thickness = 4.0
rib_offset_from_end = 20.0

outer_radius = outer_diameter / 2.0
inner_radius = outer_radius - wall_thickness

solid_body = Cylinder(outer_radius, length)
top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face])

groove = Pos(0, 0, length - groove_width / 2) * Cylinder(inner_radius - groove_depth, groove_width)
solid_body = solid_body - groove

port = Rot(0, 90, 0) * Cylinder(port_diameter / 2, outer_diameter * 2)
solid_body = solid_body - port

rib = Pos(outer_radius, 0, -length / 2 + rib_offset_from_end + rib_height / 2) * Box(rib_thickness, rib_width, rib_height)
solid_body = solid_body + rib

part = solid_body
part.name = "hollow_cylinder_with_groove_port_and_rib"
export_step(part, "output.step")