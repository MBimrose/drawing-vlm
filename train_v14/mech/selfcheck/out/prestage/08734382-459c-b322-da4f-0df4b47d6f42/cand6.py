from build123d import *

channel_width = 70.0
channel_height = 60.0
wall_thickness = 8.0
length = 80.0
fillet_radius = 2.0
hole_diameter = 6.0
hole_spacing = 20.0
hole_offset_from_end = 30.0
rib_width = 6.0
rib_height = 4.0
rib_spacing = 12.0

outer = Pos(0, 0, length/2) * Box(channel_width, channel_height, length)
inner = Pos(0, wall_thickness/2, length/2) * Box(channel_width - 2*wall_thickness, channel_height - wall_thickness, length)
base = outer - inner
base = fillet(base.edges(), fillet_radius)

rib1 = Pos(-rib_spacing/2, 0, -rib_height/2) * Box(rib_width, length, rib_height)
rib2 = Pos(rib_spacing/2, 0, -rib_height/2) * Box(rib_width, length, rib_height)
base = base + rib1 + rib2

hole_positions = [hole_offset_from_end, hole_offset_from_end + hole_spacing, hole_offset_from_end + 2*hole_spacing]
for z in hole_positions:
    base = base - Pos(channel_width/2, 0, z) * Rot(0, 90, 0) * Cylinder(hole_diameter/2, length)

part = base
part.name = "channel_with_ribs_and_holes"
export_step(part, "output.step")