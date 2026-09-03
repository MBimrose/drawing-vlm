from build123d import *

channel_length = 80.0
channel_width = 50.0
channel_height = 30.0
wall_thickness = 3.0
rib_thickness = 2.0
rib_height = 5.0
fillet_radius = 0.5
hole_diameter = 4.0
hole_spacing = 20.0
hole_count = 3

base = Pos(0, 0, channel_height/2) * Box(channel_length, channel_width, channel_height)
top_face = base.faces().sort_by(Axis.Z)[-1]
base = offset(base, amount=-wall_thickness, openings=[top_face])

rib = Pos(0, 0, wall_thickness + rib_height/2) * Box(channel_length, rib_thickness, rib_height)
result = base + rib

result = fillet(result.edges(), fillet_radius)

for i in range(hole_count):
    x = (i - (hole_count - 1) / 2) * hole_spacing
    hole = Pos(x, channel_width/2, channel_height/2) * Rot(90, 0, 0) * Cylinder(hole_diameter/2, channel_width + 10)
    result = result - hole

part = result
part.name = "channel_with_rib"
export_step(part, "output.step")