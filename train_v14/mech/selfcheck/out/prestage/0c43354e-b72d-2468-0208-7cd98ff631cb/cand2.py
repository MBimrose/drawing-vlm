from build123d import *

channel_width = 80.0
channel_height = 60.0
channel_depth = 30.0
wall_thickness = 1.0
web_thickness = 2.0
hole_diameter = 4.0
hole_spacing = 15.0
hole_offset_from_edge = 12.0

solid_body = Box(channel_width, channel_depth, channel_height)
bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[bottom_face])

web = Box(web_thickness, channel_depth - 2 * wall_thickness, channel_height - 2 * wall_thickness)
solid_body = solid_body + web

for i in range(5):
    x = -channel_width / 2 + hole_offset_from_edge + i * hole_spacing
    solid_body = solid_body - Pos(x, 0, 0) * Cylinder(hole_diameter / 2, channel_height + 10)

part = solid_body
part.name = "channel_with_web_and_holes"
export_step(part, "output.step")