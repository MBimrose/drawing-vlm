from build123d import *

channel_length = 100.0
channel_width = 30.0
channel_height = 20.0
wall_thickness = 3.0
fillet_radius = 2.0
pocket_length = 80.0
pocket_width = 10.0
pocket_depth = 2.0
pocket_offset_y = 5.0
hole_diameter = 5.0
hole_offset_x = 8.0
hole_offset_y = 8.0

solid_body = Pos(0, 0, channel_height/2) * Box(channel_length, channel_width, channel_height)
solid_body = fillet(solid_body.edges(), fillet_radius)

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face])

pocket = Pos(0, -channel_width/2 + pocket_offset_y, pocket_depth/2) * Box(pocket_length, pocket_width, pocket_depth)
solid_body = solid_body - pocket

hole = Pos(channel_length/2 - hole_offset_x, -channel_width/2 + hole_offset_y, channel_height/2) * Cylinder(hole_diameter/2, channel_height)
solid_body = solid_body - hole

part = solid_body
part.name = "channel_with_pocket_and_hole"
export_step(part, "output.step")