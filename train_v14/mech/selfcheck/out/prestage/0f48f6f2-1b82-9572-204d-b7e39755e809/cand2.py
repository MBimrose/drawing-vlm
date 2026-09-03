from build123d import *

channel_length = 80.0
channel_width = 50.0
channel_height = 30.0
wall_thickness = 3.0
rib_width = 30.0
rib_height = 10.0
chamfer_size = 2.0
hole_diameter = 5.0
hole_depth = 10.0
hole_offset_x = 15.0
hole_offset_y = 12.0

base = Pos(0, 0, channel_height/2) * Box(channel_length, channel_width, channel_height)
rib = Pos(0, 0, wall_thickness + rib_height/2) * Box(channel_length, rib_width, rib_height)
solid_body = base + rib

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face])

front_face = solid_body.faces().sort_by(Axis.X)[-1]
solid_body = chamfer(front_face.edges(), chamfer_size)

hole_r = hole_diameter / 2
hole_z = channel_height - hole_depth / 2
for x, y in [(-channel_length/2 + hole_offset_x, -channel_width/2 + hole_offset_y),
             (-channel_length/2 + hole_offset_x,  channel_width/2 - hole_offset_y),
             ( channel_length/2 - hole_offset_x, -channel_width/2 + hole_offset_y),
             ( channel_length/2 - hole_offset_x,  channel_width/2 - hole_offset_y)]:
    solid_body = solid_body - Pos(x, y, hole_z) * Cylinder(hole_r, hole_depth)

part = solid_body
part.name = "channel_with_rib"
export_step(part, "output.step")