from build123d import *

handle_length = 80
handle_width = 40
handle_height = 20
wall_thickness = 3
rib_thickness = 2
rib_spacing = 12
rib_height = handle_height - 2 * wall_thickness
chamfer_distance = 1
mount_hole_dia = 4
mount_hole_offset = 10
slot_width = 10
slot_length = 30

solid_body = Box(handle_width, handle_height, handle_length)
solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_distance)

inner = Box(handle_width - 2*wall_thickness, handle_height - 2*wall_thickness, handle_length - 2*wall_thickness)
solid_body = solid_body - inner

rib_count = int((handle_width - 2 * wall_thickness) // rib_spacing)
for i in range(rib_count):
    x_offset = -handle_width/2 + wall_thickness + rib_spacing/2 + i * rib_spacing
    rib = Pos(x_offset, 0, -handle_length/2 + rib_height/2) * Box(rib_thickness, rib_height, rib_height)
    solid_body = solid_body + rib

for x in [-handle_width/2 + mount_hole_offset, handle_width/2 - mount_hole_offset]:
    solid_body = solid_body - Pos(x, 0, 0) * Cylinder(mount_hole_dia/2, handle_length + 10)

solid_body = solid_body - Box(slot_width, slot_length, handle_length + 10)

part = solid_body
part.name = "handle"
export_step(part, "output.step")