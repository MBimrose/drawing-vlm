from build123d import *

chute_length = 80.0
chute_width = 40.0
chute_height_low = 15.0
chute_height_high = 30.0
wall_thickness = 3.0
fillet_radius = 2.0
slot_width = 4.0
slot_height = 10.0
slot_spacing = 12.0
slot_count = 3
mount_hole_dia = 5.0
mount_hole_offset = 10.0

with BuildPart() as p:
    with BuildSketch(Plane.YZ) as sk:
        with BuildLine() as bl:
            l1 = Line((0, 0), (0, chute_height_high))
            l2 = Line(l1 @ 1, (chute_width, chute_height_low))
            l3 = Line(l2 @ 1, (chute_width, 0))
            l4 = Line(l3 @ 1, (0, 0))
        make_face()
    extrude(amount=chute_length)

solid_body = p.part

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
top_edges = top_face.edges()
solid_body = fillet(top_edges, fillet_radius)

inner = offset(solid_body, amount=-wall_thickness)
solid_body = solid_body - inner

for i in range(slot_count):
    x_pos = chute_length / 2 + i * slot_spacing
    slot = Pos(x_pos, chute_width / 2, chute_height_low / 2) * Box(slot_width, chute_width + 10, slot_height)
    solid_body = solid_body - slot

hole = Pos(chute_length / 2, mount_hole_offset, chute_height_low / 2) * Rot(0, 90, 0) * Cylinder(mount_hole_dia / 2, chute_length + 10)
solid_body = solid_body - hole

part = solid_body
part.name = "chute"
export_step(part, "output.step")