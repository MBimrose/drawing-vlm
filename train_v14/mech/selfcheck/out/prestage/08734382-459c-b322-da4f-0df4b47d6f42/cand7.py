from build123d import *

outer_width = 80.0
outer_height = 60.0
wall_thickness = 8.0
length = 80.0
fillet_radius = 2.0
rib_width = 12.0
rib_height = 4.0
hole_diameter = 6.0
hole_spacing = 30.0

inner_width = outer_width - 2 * wall_thickness
inner_height = outer_height - wall_thickness

base = Pos(0, 0, length/2) * Box(outer_width, outer_height, length)
inner_cut = Pos(0, wall_thickness/2, length/2) * Box(inner_width, inner_height, length)
result = base - inner_cut
result = fillet(result.edges(), fillet_radius)

rib = Pos(0, 0, -rib_height/2) * Box(rib_width, length, rib_height)
result = result + rib

for x in [-hole_spacing/2, hole_spacing/2]:
    hole = Pos(x, 0, length/2) * Cylinder(hole_diameter/2, length)
    result = result - hole

part = result
part.name = "u_channel_with_rib"
export_step(part, "output.step")