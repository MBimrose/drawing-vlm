from build123d import *

channel_length = 100.0
channel_width = 30.0
channel_height = 20.0
wall_thickness = 3.0
groove_width = 8.0
groove_depth = 4.0
fillet_radius = 2.0
hole_diameter = 5.0
hole_offset_from_end = 8.0
hole_offset_from_bottom = 8.0

solid_body = Pos(0, 0, channel_height/2) * Box(channel_length, channel_width, channel_height)
solid_body = fillet(solid_body.edges(), fillet_radius)
top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face])

groove = Pos(0, -channel_width/2 + wall_thickness + groove_width/2, groove_depth/2) * Box(channel_length - 2*wall_thickness, groove_width, groove_depth)
solid_body = solid_body - groove

hole = Pos(channel_length/2 - wall_thickness - hole_diameter/2, -channel_length/2 + hole_offset_from_end, hole_offset_from_bottom) * Cylinder(hole_diameter/2, channel_height)
solid_body = solid_body - hole

part = solid_body
part.name = "channel_with_groove_and_hole"
export_step(part, "output.step")