from build123d import *

outer_width = 80.0
outer_height = 60.0
wall_thickness = 8.0
length = 80.0
fillet_radius = 2.0
mount_hole_dia = 5.0
mount_hole_spacing = 30.0
rib_width = 6.0
rib_height = 4.0
rib_spacing = 12.0

inner_width = outer_width - 2 * wall_thickness
inner_height = outer_height - wall_thickness

base = Pos(0, 0, length/2) * Box(outer_width, outer_height, length)
cavity = Pos(0, wall_thickness/2, length/2) * Box(inner_width, inner_height, length)
result = base - cavity
result = fillet(result.edges(), fillet_radius)

for x in [-mount_hole_spacing/2, mount_hole_spacing/2]:
    result = result - Pos(x, 0, length/2) * Cylinder(mount_hole_dia/2, length + 10)

rib1 = Pos(-rib_spacing/2, 0, -rib_height/2) * Box(rib_width, outer_width, rib_height)
rib2 = Pos(rib_spacing/2, 0, -rib_height/2) * Box(rib_width, outer_width, rib_height)
result = result + rib1 + rib2

part = result
part.name = "channel_with_ribs"
export_step(part, "output.step")