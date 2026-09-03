from build123d import *

chute_length = 80.0
chute_width = 50.0
chute_height = 30.0
wall_thickness = 3.0
rib_height = 10.0
rib_width = 30.0
rib_hole_diameter = 3.0
chamfer_distance = 2.0

base = Pos(0, 0, chute_height/2) * Box(chute_length, chute_width, chute_height)
top_face = base.faces().sort_by(Axis.Z)[-1]
hollow = offset(base, amount=-wall_thickness, openings=[top_face])

rib = Pos(0, 0, wall_thickness + rib_height/2) * Box(chute_length, rib_width, rib_height)
combined = hollow + rib

hole = Pos(0, 0, wall_thickness + rib_height/2) * Cylinder(rib_hole_diameter/2, rib_height + 1)
combined = combined - hole

x_face = combined.faces().sort_by(Axis.X)[-1]
x_edges = x_face.edges()
result = chamfer(x_edges, chamfer_distance)

part = result
part.name = "chute_with_rib"
export_step(part, "output.step")