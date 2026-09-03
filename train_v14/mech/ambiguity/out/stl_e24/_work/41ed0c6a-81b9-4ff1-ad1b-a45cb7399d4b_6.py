from build123d import *

channel_length = 80.0
channel_width = 20.0
channel_height = 30.0
wall_thickness = 2.0
chamfer_size = 1.0

solid_body = Pos(0, 0, channel_height/2) * Box(channel_length, channel_width, channel_height)
top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face])
vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = chamfer(vertical_edges, chamfer_size)

part = solid_body
part.name = "channel"
export_step(part, "output.step")