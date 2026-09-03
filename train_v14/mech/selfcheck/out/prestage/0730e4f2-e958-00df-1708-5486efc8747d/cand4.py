from build123d import *

outer_width = 80.0
outer_depth = 60.0
outer_height = 40.0
wall_thickness = 2.0
rib_thickness = 2.0
fillet_radius = 3.0
hole_diameter = 4.0
hole_spacing_x = 20.0
hole_spacing_y = 15.0
hole_rows = 2
hole_cols = 3

inner_width = outer_width - 2 * wall_thickness
inner_depth = outer_depth - 2 * wall_thickness
inner_height = outer_height - 2 * wall_thickness

outer_box = Pos(0, 0, outer_height/2) * Box(outer_width, outer_depth, outer_height)
inner_box = Pos(0, 0, outer_height/2) * Box(inner_width, inner_depth, inner_height)
shell = outer_box - inner_box

rib = Pos(0, 0, wall_thickness + inner_height/2) * Box(inner_width, rib_thickness, inner_height)
result = shell + rib

result = fillet(result.edges().filter_by(Axis.Z), fillet_radius)

for i in range(hole_cols):
    for j in range(hole_rows):
        x = (i - (hole_cols-1)/2) * hole_spacing_x
        z = (j - (hole_rows-1)/2) * hole_spacing_y + outer_height/2
        result = result - Pos(x, outer_depth/2, z) * Rot(90, 0, 0) * Cylinder(hole_diameter/2, outer_depth + 10)

part = result
part.name = "hollow_box_with_rib_and_holes"
export_step(part, "output.step")