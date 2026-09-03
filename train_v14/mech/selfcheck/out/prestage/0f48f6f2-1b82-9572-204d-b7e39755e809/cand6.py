from build123d import *

chute_length = 80.0
chute_width = 50.0
chute_height = 30.0
wall_thickness = 3.0
rib_height = 10.0
rib_width = 30.0
chamfer_distance = 2.0

outer = Pos(0, 0, chute_height/2) * Box(chute_length, chute_width, chute_height)
inner = Pos(0, 0, wall_thickness + (chute_height - wall_thickness)/2) * Box(chute_length - 2*wall_thickness, chute_width - 2*wall_thickness, chute_height - wall_thickness)
rib = Pos(0, 0, wall_thickness + rib_height/2) * Box(chute_length, rib_width, rib_height)

solid_body = outer - inner + rib

x_face = solid_body.faces().sort_by(Axis.X)[-1]
x_edges = x_face.edges()
solid_body = chamfer(x_edges, chamfer_distance)

part = solid_body
part.name = "chute"
export_step(part, "output.step")