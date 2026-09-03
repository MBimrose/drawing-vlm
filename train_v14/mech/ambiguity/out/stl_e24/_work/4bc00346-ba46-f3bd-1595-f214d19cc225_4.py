from build123d import *

channel_length = 80.0
channel_width = 20.0
channel_height = 30.0
wall_thickness = 1.0
groove_width = 12.0
groove_depth = 4.0
hole_diameter = 5.5
hole_spacing = 15.0
chamfer_size = 0.5

solid_body = Box(channel_length, channel_width, channel_height)
top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face])

groove = Pos(0, 0, channel_height - groove_depth/2) * Box(groove_width, channel_width, groove_depth)
solid_body = solid_body - groove

hole_r = hole_diameter / 2
for y in [-hole_spacing/2, hole_spacing/2]:
    hole = Pos(-channel_length/2, 0, y) * Rot(0, 90, 0) * Cylinder(hole_r, channel_length)
    solid_body = solid_body - hole

vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = chamfer(vertical_edges, chamfer_size)

part = solid_body
part.name = "channel_with_groove_and_holes"
export_step(part, "output.step")