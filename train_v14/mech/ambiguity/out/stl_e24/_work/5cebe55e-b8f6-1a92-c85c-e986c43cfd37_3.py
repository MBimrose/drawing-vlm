from build123d import *

channel_length = 80.0
channel_height = 30.0
channel_width = 20.0
wall_thickness = 1.0
vent_slot_width = 4.0
vent_slot_height = 12.0
vent_slot_offset_from_bottom = 8.0
hole_diameter = 4.0
countersink_diameter = 7.0
countersink_angle = 82.0
hole_spacing = 12.0
hole_count = 3
hole_offset_from_start = 20.0

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

vent_slot = Pos(channel_length - wall_thickness * 1.5 / 2, channel_height / 2 + vent_slot_offset_from_bottom + vent_slot_height / 2, channel_width / 2 + channel_height / 2) * Box(wall_thickness * 1.5, vent_slot_width, vent_slot_height)
solid_body = solid_body - vent_slot

for i in range(hole_count):
    x = hole_offset_from_start + i * hole_spacing
    hole = Pos(x, channel_height / 2, channel_width) * CounterSinkHole(hole_diameter / 2, countersink_diameter / 2, channel_width, countersink_angle)
    solid_body = solid_body - hole

part = solid_body
part.name = "channel_with_vent_and_holes"
export_step(part, "output.step")