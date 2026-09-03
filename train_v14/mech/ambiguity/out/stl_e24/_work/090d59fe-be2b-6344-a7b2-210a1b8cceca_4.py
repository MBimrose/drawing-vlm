from build123d import *

channel_length = 80.0
channel_width = 40.0
channel_height = 30.0
wall_thickness = 3.0
slot_width = 4.0
slot_height = 10.0
slot_spacing = 12.0
num_slots = 3
chamfer_size = 1.0
hole_diameter = 5.0
hole_offset_y = 10.0

with BuildPart() as p:
    with BuildSketch(Plane.YZ) as sk:
        with BuildLine() as bl:
            l1 = Line((0, 0), (0, channel_height))
            l2 = Line(l1 @ 1, (channel_width, channel_height / 2))
            l3 = Line(l2 @ 1, (channel_width, 0))
            l4 = Line(l3 @ 1, (0, 0))
        make_face()
    extrude(amount=channel_length)

solid_body = p.part
top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face])

top_edges = solid_body.edges().sort_by(Axis.Z)[-4:]
solid_body = chamfer(top_edges, chamfer_size)

for i in range(num_slots):
    x_pos = channel_length / 2 + i * slot_spacing
    solid_body = solid_body - Pos(x_pos, channel_width / 2, channel_height / 2) * Box(slot_width, channel_width + 10, slot_height)

solid_body = solid_body - Pos(channel_length / 2, hole_offset_y, channel_height / 2) * Rot(0, 90, 0) * Cylinder(hole_diameter / 2, channel_length + 10)

part = solid_body
part.name = "channel_with_slots_and_hole"
export_step(part, "output.step")