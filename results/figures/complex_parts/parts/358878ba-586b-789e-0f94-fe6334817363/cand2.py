from build123d import *

channel_length = 80.0
channel_width = 30.0
channel_height = 40.0
wall_thickness = 2.0
vent_slot_width = 6.0
vent_slot_height = 10.0
vent_slot_spacing = 12.0
vent_slot_count = 3
chamfer_distance = 0.5

solid_body = Box(channel_length, channel_width, channel_height)
top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face])

for i in range(vent_slot_count):
    x_offset = (i - (vent_slot_count - 1) / 2) * vent_slot_spacing
    slot = Pos(x_offset, channel_width/2 - wall_thickness/2, channel_height/2 - vent_slot_height/2) * Box(vent_slot_width, wall_thickness, vent_slot_height)
    solid_body = solid_body - slot

for i in range(vent_slot_count):
    x_offset = (i - (vent_slot_count - 1) / 2) * vent_slot_spacing
    slot = Pos(x_offset, -channel_width/2 + wall_thickness/2, channel_height/2 - vent_slot_height/2) * Box(vent_slot_width, wall_thickness, vent_slot_height)
    solid_body = solid_body - slot

front_face = solid_body.faces().sort_by(Axis.X)[-1]
front_vertical_edges = front_face.edges().filter_by(Axis.Z)
solid_body = chamfer(front_vertical_edges, chamfer_distance)

part = solid_body
part.name = "vented_channel"
export_step(part, "output.step")