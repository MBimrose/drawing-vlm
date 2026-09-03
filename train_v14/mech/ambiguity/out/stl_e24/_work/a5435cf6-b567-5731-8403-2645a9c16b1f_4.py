from build123d import *

channel_length = 80.0
channel_width = 40.0
channel_height = 20.0
wall_thickness = 3.0
rib_thickness = 2.0
rib_height = 10.0
rib_spacing = 10.0
rib_count = 3
chamfer_size = 1.0

outer = Pos(0, 0, channel_length/2) * Box(channel_width, channel_height, channel_length)
inner = Pos(0, 0, (channel_length - wall_thickness)/2) * Box(channel_width - 2*wall_thickness, channel_height - 2*wall_thickness, channel_length - wall_thickness)
channel = outer - inner

channel = chamfer(channel.edges().filter_by(Axis.Z), chamfer_size)

for i in range(rib_count):
    x_offset = -channel_width/2 + wall_thickness + rib_spacing/2 + i * rib_spacing
    rib = Pos(x_offset, 0, channel_height/2 - wall_thickness - rib_height/2) * Box(rib_thickness, rib_height, channel_length - 2*wall_thickness)
    channel = channel + rib

part = channel
part.name = "channel_with_ribs"
export_step(part, "output.step")