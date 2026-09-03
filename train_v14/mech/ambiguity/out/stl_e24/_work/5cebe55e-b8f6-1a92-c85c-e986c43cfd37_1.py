from build123d import *

channel_length = 80.0
channel_height = 30.0
channel_width = 20.0
wall_thickness = 1.0
slot_width = 4.0
slot_length = 15.0
hole_diameter = 4.0
hole_spacing = 12.0
chamfer_size = 0.5

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            l1 = Line((0, 0), (0, channel_height))
            l2 = ThreePointArc(l1 @ 1, (channel_length / 2, channel_height + 5), (channel_length, channel_height))
            l3 = Line(l2 @ 1, (channel_length, 0))
            l4 = Line(l3 @ 1, (0, 0))
        make_face()
    extrude(amount=channel_width)

solid_body = p.part
bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[bottom_face])

slot_cut = Pos(channel_length - slot_width / 2, channel_height - slot_width / 2, channel_width - slot_length / 2) * Box(slot_width, slot_width, slot_length)
solid_body = solid_body - slot_cut

for i in range(3):
    x = channel_length / 2 + (i - 1) * hole_spacing
    y = channel_height / 2
    hole_cut = Pos(x, y, channel_width / 2) * Cylinder(hole_diameter / 2, channel_width + 10)
    solid_body = solid_body - hole_cut

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
top_edges = top_face.edges()
solid_body = chamfer(top_edges, chamfer_size)

part = solid_body
part.name = "channel_with_slot_and_holes"
export_step(part, "output.step")