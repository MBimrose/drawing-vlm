from build123d import *

channel_length = 80.0
channel_width = 40.0
channel_height = 20.0
wall_thickness = 3.0
rib_thickness = 2.0
rib_width = 10.0
rib_spacing = 12.0
rib_length = 30.0
chamfer_distance = 1.0
hole_diameter = 5.0
hole_spacing = 20.0

base = Pos(0, 0, channel_length/2) * Box(channel_width, channel_height, channel_length)
bottom_face = base.faces().sort_by(Axis.Z)[0]
base = offset(base, amount=-wall_thickness, openings=[bottom_face])
base = chamfer(base.edges().filter_by(Axis.Z), chamfer_distance)

interior_width = channel_width - 2 * wall_thickness
rib_count = int(interior_width // rib_spacing)
for i in range(rib_count):
    x = (i - (rib_count - 1) / 2) * rib_spacing
    base = base + Pos(x, 0, rib_length/2) * Box(rib_thickness, rib_width, rib_length)

for x in [-hole_spacing/2, hole_spacing/2]:
    base = base - Pos(x, 0, channel_length/2) * Cylinder(hole_diameter/2, channel_length)

part = base
part.name = "channel_with_ribs"
export_step(part, "output.step")