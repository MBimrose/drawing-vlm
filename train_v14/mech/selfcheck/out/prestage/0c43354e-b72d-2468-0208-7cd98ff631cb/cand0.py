from build123d import *

channel_length = 80.0
channel_width = 30.0
channel_height = 60.0
wall_thickness = 1.0
rib_thickness = 2.0
hole_diameter = 4.0
hole_spacing = 15.0
hole_offset_from_end = 12.0

base = Pos(0, 0, channel_height/2) * Box(channel_length, channel_width, channel_height)
bottom_face = base.faces().sort_by(Axis.Z)[0]
shell_body = offset(base, amount=-wall_thickness, openings=[bottom_face])

rib = Pos(0, 0, channel_height/2) * Box(rib_thickness, channel_width - 2*wall_thickness, channel_height)
combined = shell_body + rib

hole_positions = [(-channel_length/2 + hole_offset_from_end + i*hole_spacing, 0) for i in range(3)]
for x, y in hole_positions:
    combined = combined - Pos(x, y, channel_height/2) * Cylinder(hole_diameter/2, channel_height + 10)

part = combined
part.name = "channel_with_rib_and_holes"
export_step(part, "output.step")