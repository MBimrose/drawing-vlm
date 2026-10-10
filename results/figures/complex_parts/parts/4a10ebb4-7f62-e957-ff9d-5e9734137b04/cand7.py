from build123d import *

enclosure_length = 80.0
enclosure_width = 50.0
enclosure_height = 30.0
wall_thickness = 2.0
rib_height = 4.0
rib_thickness = 2.0
socket_width = 20.0
socket_length = 30.0
socket_depth = 12.0
socket_chamfer = 1.0

base = Pos(0, 0, enclosure_height / 2) * Box(enclosure_length, enclosure_width, enclosure_height)
bottom_face = base.faces().sort_by(Axis.Z)[0]
base = offset(base, amount=-wall_thickness, openings=[bottom_face])

rib = Pos(0, 0, -rib_height / 2) * Box(enclosure_length - 2 * wall_thickness, rib_thickness, rib_height)
base = base + rib

socket = Pos(0, 0, enclosure_height - socket_depth / 2) * Box(socket_width, socket_length, socket_depth)
socket_edges = socket.edges().filter_by(Axis.Z)
socket = chamfer(socket_edges, socket_chamfer)
base = base - socket

part = base
part.name = "enclosure_with_socket"
export_step(part, "output.step")