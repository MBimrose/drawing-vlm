from build123d import *

outer_length = 80.0
outer_width = 50.0
outer_height = 30.0
wall_thickness = 2.0
base_thickness = 8.0
socket_length = 30.0
socket_width = 20.0
socket_depth = 12.0
vent_slot_width = 6.0
vent_slot_height = 10.0
mount_hole_dia = 2.0
mount_hole_offset = 5.0
chamfer_size = 0.5

solid_body = Pos(0, 0, outer_height/2) * Box(outer_length, outer_width, outer_height)

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face, bottom_face])

base_plate = Pos(0, 0, base_thickness/2) * Box(outer_length - 2*wall_thickness, outer_width - 2*wall_thickness, base_thickness)
solid_body = solid_body + base_plate

socket_cut = Pos(0, 0, outer_height - socket_depth/2) * Box(socket_length, socket_width, socket_depth)
solid_body = solid_body - socket_cut

vent_cut = Box(wall_thickness + 0.2, vent_slot_width, vent_slot_height)
solid_body = solid_body - Pos(outer_length/2 - wall_thickness/2, 0, outer_height/2) * vent_cut
solid_body = solid_body - Pos(-outer_length/2 + wall_thickness/2, 0, outer_height/2) * vent_cut

hole_positions = [
    (outer_length/2 - mount_hole_offset, outer_width/2 - mount_hole_offset),
    (-outer_length/2 + mount_hole_offset, outer_width/2 - mount_hole_offset),
    (-outer_length/2 + mount_hole_offset, -outer_width/2 + mount_hole_offset),
    (outer_length/2 - mount_hole_offset, -outer_width/2 + mount_hole_offset),
]
for x, y in hole_positions:
    solid_body = solid_body - Pos(x, y, outer_height/2) * Cylinder(mount_hole_dia/2, outer_height + 1)

top_edges = solid_body.edges().sort_by(Axis.Z)[-1:]
solid_body = chamfer(top_edges, chamfer_size)

part = solid_body
part.name = "enclosure_with_socket_and_vents"
export_step(part, "output.step")