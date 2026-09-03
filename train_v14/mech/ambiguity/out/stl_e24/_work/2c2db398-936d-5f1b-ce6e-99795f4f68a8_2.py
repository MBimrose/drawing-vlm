from build123d import *

plate_width = 80.0
plate_depth = 60.0
plate_thickness = 8.0
rib_width = 10.0
rib_height = 30.0
rib_offset = 5.0
socket_radius = 12.0
socket_depth = 20.0
socket_offset_x = 20.0
socket_offset_y = 0.0
fillet_radius = 2.0

base = Pos(0, 0, plate_thickness/2) * Box(plate_width, plate_depth, plate_thickness)
rib = Pos(-plate_width/2 + rib_offset + rib_width/2, 0, plate_thickness/2) * Box(rib_width, rib_height, plate_thickness)
solid_body = base + rib

socket = Pos(socket_offset_x, socket_offset_y, plate_thickness) * Cylinder(socket_radius, socket_depth)
solid_body = solid_body - socket

vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = fillet(vertical_edges, fillet_radius)

part = solid_body
part.name = "plate_with_rib_and_socket"
export_step(part, "output.step")