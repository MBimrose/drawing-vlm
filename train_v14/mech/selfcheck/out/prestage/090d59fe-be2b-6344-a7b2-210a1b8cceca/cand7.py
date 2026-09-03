from build123d import *

chute_length = 80.0
chute_width = 40.0
chute_height = 30.0
wall_thickness = 3.0
fillet_radius = 2.0
mount_hole_dia = 5.0
mount_hole_offset = 10.0
slot_width = 4.0
slot_height = 10.0
slot_spacing = 12.0
slot_count = 3

with BuildPart() as p:
    with BuildSketch(Plane.YZ) as sk:
        with BuildLine() as bl:
            Polyline((0, 0), (chute_width, 0), (chute_width, chute_height * 0.6), (0, chute_height), close=True)
        make_face()
    extrude(amount=chute_length)

solid_body = p.part

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face])

top_edges = solid_body.edges().sort_by(Axis.Z)[-4:]
solid_body = fillet(top_edges, fillet_radius)

hole = Rot(0, 90, 0) * Cylinder(mount_hole_dia / 2, chute_length + 10)
solid_body = solid_body - Pos(chute_length / 2, mount_hole_offset, chute_height / 2) * hole

for i in range(slot_count):
    x_pos = chute_length / 2 + i * slot_spacing
    slot = Box(slot_width, wall_thickness + 0.5, slot_height)
    solid_body = solid_body - Pos(x_pos, chute_width / 2, chute_height / 2) * slot
    solid_body = solid_body - Pos(x_pos, -chute_width / 2, chute_height / 2) * slot

part = solid_body
part.name = "chute"
export_step(part, "output.step")