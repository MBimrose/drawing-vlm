from build123d import *

channel_length = 80.0
channel_width = 20.0
channel_height = 30.0
wall_thickness = 2.0
pocket_length = 30.0
pocket_width = 12.0
pocket_depth = 8.0
blind_hole_diameter = 5.0
blind_hole_depth = 10.0
chamfer_size = 1.0

solid_body = Pos(0, 0, channel_height / 2) * Box(channel_length, channel_width, channel_height)
top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face])

pocket = Pos(0, 0, channel_height - pocket_depth / 2) * Box(pocket_length, pocket_width, pocket_depth)
solid_body = solid_body - pocket

hole = Pos(0, 0, channel_height - blind_hole_depth / 2) * Cylinder(blind_hole_diameter / 2, blind_hole_depth)
solid_body = solid_body - hole

vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = chamfer(vertical_edges, chamfer_size)

part = solid_body
part.name = "channel_with_pocket_and_hole"
export_step(part, "output.step")