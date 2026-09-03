from build123d import *

channel_length = 80.0
channel_width = 40.0
channel_height = 30.0
wall_thickness = 2.5
groove_width = 20.0
groove_depth = 4.0
fillet_radius = 1.2
hole_diameter = 5.0
hole_spacing = 30.0
rib_width = 6.0
rib_height = 4.0
rib_spacing = 15.0
rib_offset = 10.0

solid_body = Pos(0, 0, channel_height/2) * Box(channel_length, channel_width, channel_height)

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face, bottom_face])

groove = Pos(0, 0, channel_height - groove_depth/2) * Box(groove_width, groove_depth, groove_depth)
solid_body = solid_body - groove

solid_body = fillet(solid_body.edges().filter_by(Axis.Z), fillet_radius)

for x in [-hole_spacing/2, hole_spacing/2]:
    solid_body = solid_body - Pos(x, 0, channel_height/2) * Cylinder(hole_diameter/2, channel_height)

num_ribs = int((channel_length - 2 * rib_offset) // rib_spacing) + 1
for i in range(num_ribs):
    x_pos = -channel_length/2 + rib_offset + i * rib_spacing
    rib = Pos(x_pos, 0, rib_height/2) * Box(rib_width, rib_height, rib_height)
    solid_body = solid_body + rib

part = solid_body
part.name = "channel_with_groove_holes_ribs"
export_step(part, "output.step")