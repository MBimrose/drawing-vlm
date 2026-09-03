from build123d import *

chute_length = 80.0
chute_width = 50.0
chute_height = 30.0
wall_thickness = 3.0
rib_thickness = 2.0
rib_height = 5.0
fillet_radius = 0.5
hole_diameter = 4.0
hole_spacing = 20.0
hole_count = 3

solid_body = Pos(0, 0, chute_height / 2) * Box(chute_length, chute_width, chute_height)

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face])

rib = Pos(0, 0, wall_thickness + rib_height / 2) * Box(chute_length, rib_thickness, rib_height)
solid_body = solid_body + rib

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
top_edges = top_face.edges()
solid_body = fillet(top_edges, fillet_radius)

for i in range(hole_count):
    x = (i - (hole_count - 1) / 2) * hole_spacing
    solid_body = solid_body - Pos(x, chute_width / 2, chute_height / 2) * Rot(90, 0, 0) * Cylinder(hole_diameter / 2, chute_width + 10)
    solid_body = solid_body - Pos(x, -chute_width / 2, chute_height / 2) * Rot(90, 0, 0) * Cylinder(hole_diameter / 2, chute_width + 10)

part = solid_body
part.name = "chute"
export_step(part, "output.step")