from build123d import *

channel_length = 80.0
channel_width = 50.0
channel_height = 30.0
wall_thickness = 3.0
chamfer_distance = 2.0
hole_diameter = 4.0
hole_spacing = 30.0

solid_body = Pos(0, 0, channel_height/2) * Box(channel_length, channel_width, channel_height)

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face])

bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
bottom_edges = bottom_face.edges()
solid_body = chamfer(bottom_edges, chamfer_distance)

for y_pos in [-hole_spacing/2, hole_spacing/2]:
    hole = Pos(channel_length/2, y_pos, channel_height/2) * Rot(0, 90, 0) * Cylinder(hole_diameter/2, channel_length + 10)
    solid_body = solid_body - hole

part = solid_body
part.name = "channel"
export_step(part, "output.step")