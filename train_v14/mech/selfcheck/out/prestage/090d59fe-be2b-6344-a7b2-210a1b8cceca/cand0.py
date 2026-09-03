from build123d import *

chute_length = 80.0
chute_width = 40.0
chute_height_start = 30.0
chute_height_end = 15.0
wall_thickness = 3.0
fillet_radius = 2.0
slot_width = 4.0
slot_height = 10.0
slot_spacing = 12.0
num_slots = 3
mount_hole_dia = 5.0
mount_hole_offset = 10.0
rib_thickness = 2.0

with BuildPart() as p:
    with BuildSketch(Plane.YZ) as sk:
        with BuildLine() as bl:
            l1 = Line((0, 0), (0, chute_height_start))
            l2 = Line(l1 @ 1, (chute_width, chute_height_end))
            l3 = Line(l2 @ 1, (chute_width, 0))
            l4 = Line(l3 @ 1, (0, 0))
        make_face()
    extrude(amount=chute_length)

solid_body = p.part
top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face])

top_edges = solid_body.edges().sort_by(Axis.Z)[-4:]
solid_body = fillet(top_edges, fillet_radius)

for i in range(num_slots):
    x_pos = chute_length / 2 + i * slot_spacing
    slot = Pos(x_pos, chute_width / 2, chute_height_end / 2) * Box(slot_width, chute_width + 10, slot_height)
    solid_body = solid_body - slot

mount_hole = Pos(0, mount_hole_offset, chute_height_start / 2) * Rot(0, 90, 0) * Cylinder(mount_hole_dia / 2, chute_length + 10)
solid_body = solid_body - mount_hole

rib = Pos(chute_length / 2, chute_width / 2, wall_thickness + rib_thickness / 2) * Box(chute_length - 2 * wall_thickness, rib_thickness, rib_thickness)
solid_body = solid_body + rib

part = solid_body
part.name = "chute"
export_step(part, "output.step")