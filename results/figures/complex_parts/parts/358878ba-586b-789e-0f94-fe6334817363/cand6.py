from build123d import *

channel_length = 80.0
channel_width = 30.0
channel_height = 40.0
wall_thickness = 2.0
slot_width = 6.0
slot_height = 10.0
slot_spacing = 12.0
slot_count = 4
chamfer_size = 0.5

solid_body = Pos(0, 0, channel_height/2) * Box(channel_length, channel_width, channel_height)

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face])

for i in range(slot_count):
    x = (i - (slot_count - 1) / 2) * slot_spacing
    slot = Pos(x, 0, channel_height - slot_height/2) * Box(slot_width, channel_width, slot_height)
    solid_body = solid_body - slot

x_face = solid_body.faces().sort_by(Axis.X)[-1]
x_edges = x_face.edges()
solid_body = chamfer(x_edges, chamfer_size)

part = solid_body
part.name = "channel_with_slots"
export_step(part, "output.step")