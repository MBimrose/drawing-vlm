from build123d import *

chute_length = 80.0
chute_width = 40.0
chute_height_rear = 30.0
chute_height_front = 15.0
wall_thickness = 3.0
vent_slot_width = 4.0
vent_slot_height = 10.0
vent_slot_spacing = 12.0
vent_slot_count = 3
mount_hole_dia = 5.0
mount_hole_offset = 10.0
chamfer_size = 1.0

with BuildPart() as p:
    with BuildSketch(Plane.YZ) as sk:
        with BuildLine() as bl:
            l1 = Line((0, 0), (0, chute_height_rear))
            l2 = Line(l1 @ 1, (chute_width, chute_height_front))
            l3 = Line(l2 @ 1, (chute_width, 0))
            l4 = Line(l3 @ 1, (0, 0))
        make_face()
    extrude(amount=chute_length)

solid_body = p.part
top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face])

top_edges = solid_body.edges().sort_by(Axis.Z)[-4:]
solid_body = chamfer(top_edges, chamfer_size)

for i in range(vent_slot_count):
    x_pos = chute_length/2 + i * vent_slot_spacing
    solid_body = solid_body - Pos(x_pos, chute_width/2, chute_height_front/2) * Box(vent_slot_width, chute_width + 10, vent_slot_height)

for i in range(vent_slot_count):
    x_pos = chute_length/2 + i * vent_slot_spacing
    solid_body = solid_body - Pos(x_pos, 0, chute_height_rear/2) * Box(vent_slot_width, chute_width + 10, vent_slot_height)

solid_body = solid_body - Pos(0, mount_hole_offset, chute_height_rear/2) * Rot(0, 90, 0) * Cylinder(mount_hole_dia/2, chute_length + 10)

part = solid_body
part.name = "chute"
export_step(part, "output.step")