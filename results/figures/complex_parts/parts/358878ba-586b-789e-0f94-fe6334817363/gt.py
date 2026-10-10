from build123d import *

channel_length = 80.0
channel_width = 30.0
channel_height = 40.0
wall_thickness = 2.0
top_open_width = channel_width - 2 * wall_thickness
slot_width = 6.0
slot_height = 12.0
slot_spacing = 20.0
lip_chamfer = 0.5

base = Pos(0, 0, channel_height / 2) * Box(channel_length, channel_width, channel_height)

top_face = base.faces().sort_by(Axis.Z)[-1]
base = offset(base, amount=-wall_thickness, openings=[top_face])

top_cut = Pos(0, 0, channel_height - wall_thickness) * Box(top_open_width, channel_length, wall_thickness * 2)
base = base - top_cut

for x in [slot_spacing / 2, -slot_spacing / 2]:
    z = channel_height / 2 + (channel_height / 2 - slot_height / 2 - wall_thickness)
    side_cut = Pos(x, channel_width / 2 - wall_thickness, z) * Box(slot_width, wall_thickness * 2, slot_height)
    base = base - side_cut

top_edges = base.edges().sort_by(Axis.X)[-2:]
base = chamfer(top_edges, lip_chamfer)

part = base
part.name = "channel"
export_step(part, OUTPUT_PATH)