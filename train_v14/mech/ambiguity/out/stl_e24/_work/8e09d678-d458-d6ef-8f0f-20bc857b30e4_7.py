from build123d import *

outer_length = 80.0
outer_width = 50.0
outer_height = 20.0
wall_thickness = 2.0
socket_width = 15.0
socket_height = 10.0
socket_depth = 5.0
chamfer_distance = 1.5
mount_hole_dia = 3.0
mount_hole_spacing_x = 50.0
mount_hole_spacing_y = 40.0

solid_body = Pos(0, 0, outer_height/2) * Box(outer_length, outer_width, outer_height)

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face])

socket_cut = Pos(0, outer_width/2 - socket_depth/2, outer_height/2 - socket_height/2) * Box(socket_width, socket_depth, socket_height)
solid_body = solid_body - socket_cut

rear_edges = solid_body.edges().filter_by(Axis.Z).sort_by(Axis.Y)[:2]
solid_body = chamfer(rear_edges, chamfer_distance)

for x in [-mount_hole_spacing_x/2, mount_hole_spacing_x/2]:
    for y in [-mount_hole_spacing_y/2, mount_hole_spacing_y/2]:
        hole = Pos(x, y, outer_height/2) * Cylinder(mount_hole_dia/2, outer_height)
        solid_body = solid_body - hole

part = solid_body
part.name = "shelled_box_with_socket"
export_step(part, "output.step")