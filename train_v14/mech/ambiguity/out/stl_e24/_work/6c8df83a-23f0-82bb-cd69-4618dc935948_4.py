from build123d import *

channel_length = 80.0
channel_width = 50.0
channel_height = 30.0
wall_thickness = 3.0
rib_height = 5.0
rib_thickness = 2.0
hole_diameter = 4.0
hole_spacing = 20.0
hole_offset_from_end = 10.0
fillet_radius = 0.5

base = Pos(0, 0, channel_height/2) * Box(channel_length, channel_width, channel_height)
top_face = base.faces().sort_by(Axis.Z)[-1]
base = offset(base, amount=-wall_thickness, openings=[top_face])

rib = Pos(0, 0, wall_thickness + rib_height/2) * Box(channel_length, rib_thickness, rib_height)
result = base + rib

hole_positions = [(-channel_length/2 + hole_offset_from_end + i*hole_spacing, 0) for i in range(3)]
for x, y in hole_positions:
    result = result - Pos(x, channel_width/2, channel_height/2) * Rot(90, 0, 0) * Cylinder(hole_diameter/2, channel_width + 10)

top_face = result.faces().sort_by(Axis.Z)[-1]
result = fillet(top_face.edges(), fillet_radius)

part = result
part.name = "channel_with_rib"
export_step(part, "output.step")