from build123d import *

chute_length = 80.0
chute_width = 40.0
chute_height = 30.0
wall_thickness = 2.5
base_thickness = 2.0
channel_width = 20.0
channel_depth = 10.0
rib_width = 6.0
rib_height = 4.0
rib_spacing = 15.0
fillet_radius = 1.2

base = Pos(0, 0, base_thickness/2) * Box(chute_length, chute_width, base_thickness)

outer = Pos(0, 0, chute_height/2) * Box(chute_length, chute_width, chute_height)
inner = Pos(0, 0, chute_height/2) * Box(chute_length - 2*wall_thickness, chute_width - 2*wall_thickness, chute_height)
walls = outer - inner

result = base + walls

channel = Pos(0, 0, chute_height - channel_depth/2) * Box(chute_length, channel_width, channel_depth)
result = result - channel

result = fillet(result.edges().filter_by(Axis.Z), fillet_radius)

num_ribs = int((chute_length - 2*wall_thickness) // rib_spacing) + 1
for i in range(num_ribs):
    x = (i - (num_ribs - 1) / 2) * rib_spacing
    rib = Pos(x, 0, rib_height/2) * Box(rib_width, rib_height, rib_height)
    result = result + rib

part = result
part.name = "chute"
export_step(part, "output.step")