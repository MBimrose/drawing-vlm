from build123d import *

channel_width = 80.0
channel_height = 60.0
channel_length = 80.0
wall_thickness = 8.0
notch_width = 30.0
notch_depth = 12.0
fillet_radius = 2.0
rib_width = 6.0
rib_height = 10.0
rib_spacing = 20.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline(
                (-channel_width/2, 0),
                (channel_width/2, 0),
                (channel_width/2, channel_height),
                (channel_width/2 - wall_thickness, channel_height),
                (channel_width/2 - wall_thickness, wall_thickness),
                (-channel_width/2 + wall_thickness, wall_thickness),
                (-channel_width/2 + wall_thickness, channel_height),
                (-channel_width/2, channel_height),
                close=True
            )
        make_face()
    extrude(amount=channel_length)

solid_body = p.part
solid_body = fillet(solid_body.edges(), fillet_radius)

notch_box = Pos(0, channel_height/2, channel_length/2) * Box(notch_width, notch_depth, channel_length)
solid_body = solid_body - notch_box

rib_count = int((channel_width - 2*wall_thickness) // rib_spacing) + 1
for i in range(rib_count):
    x_pos = -channel_width/2 + wall_thickness + i * rib_spacing
    rib = Pos(x_pos, channel_height/2, 0) * Box(rib_width, channel_length, rib_height)
    solid_body = solid_body + rib

part = solid_body
part.name = "u_channel_with_ribs"
export_step(part, "output.step")