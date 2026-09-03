from build123d import *

channel_length = 80.0
channel_width = 30.0
channel_height = 40.0
wall_thickness = 2.0
pocket_width = 20.0
pocket_depth = 10.0
slot_width = 6.0
slot_length = 20.0
slot_offset = 10.0
chamfer_size = 0.5

solid_body = Pos(0, 0, channel_height/2) * Box(channel_length, channel_width, channel_height)

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face])

pocket = Pos(0, 0, channel_height - pocket_depth/2) * Box(pocket_width, pocket_depth, pocket_depth)
solid_body = solid_body - pocket

slot1 = Pos(-channel_length/2 + slot_offset + slot_width/2, 0, channel_height - pocket_depth/2) * Box(slot_width, slot_length, pocket_depth)
solid_body = solid_body - slot1

slot2 = Pos(channel_length/2 - slot_offset - slot_width/2, 0, channel_height - pocket_depth/2) * Box(slot_width, slot_length, pocket_depth)
solid_body = solid_body - slot2

front_face = solid_body.faces().sort_by(Axis.X)[-1]
front_edges = front_face.edges()
solid_body = chamfer(front_edges, chamfer_size)

part = solid_body
part.name = "channel_with_pocket_and_slots"
export_step(part, "output.step")