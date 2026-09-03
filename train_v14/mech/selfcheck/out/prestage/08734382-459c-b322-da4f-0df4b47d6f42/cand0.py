from build123d import *

outer_width = 80.0
outer_height = 60.0
wall_thickness = 8.0
channel_length = 80.0
fillet_radius = 2.0
slot_width = 12.0
slot_depth = 4.0
hole_diameter = 5.0
hole_spacing = 30.0
rib_width = 6.0
rib_height = 4.0
rib_spacing = 15.0

inner_width = outer_width - 2 * wall_thickness
inner_height = outer_height - wall_thickness

result = Box(outer_width, outer_height, channel_length)

cavity = Pos(0, wall_thickness / 2, 0) * Box(inner_width, inner_height, channel_length)
result = result - cavity

result = fillet(result.edges(), fillet_radius)

slot = Pos(0, -outer_height / 2 + slot_depth / 2, 0) * Box(slot_width, slot_depth, channel_length)
result = result - slot

for x in [-hole_spacing / 2, hole_spacing / 2]:
    result = result - Pos(x, 0, 0) * Cylinder(hole_diameter / 2, channel_length)

for x in [-rib_spacing / 2, rib_spacing / 2]:
    rib = Pos(x, 0, -channel_length / 2 - rib_height / 2) * Box(rib_width, channel_length, rib_height)
    result = result + rib

part = result
part.name = "channel_with_ribs"
export_step(part, "output.step")