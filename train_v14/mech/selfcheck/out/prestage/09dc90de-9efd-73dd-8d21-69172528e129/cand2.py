from build123d import *

outer_width = 50.0
outer_length = 80.0
outer_height = 30.0
wall_thickness = 4.0
fillet_radius = 2.0
hole_diameter = 5.0
hole_spacing_x = 12.0
hole_spacing_y = 12.0
hole_rows = 3
hole_cols = 4

base = Pos(0, 0, outer_height / 2) * Box(outer_width, outer_length, outer_height)
base = fillet(base.edges(), fillet_radius)

inner_width = outer_width - 2 * wall_thickness
inner_length = outer_length - 2 * wall_thickness
inner_height = outer_height - wall_thickness
cavity = Pos(0, 0, wall_thickness + inner_height / 2) * Box(inner_width, inner_length, inner_height)
base = base - cavity

for i in range(hole_cols):
    for j in range(hole_rows):
        x = (i - (hole_cols - 1) / 2) * hole_spacing_x
        y = (j - (hole_rows - 1) / 2) * hole_spacing_y
        hole = Pos(x, y, outer_height / 2) * Cylinder(hole_diameter / 2, outer_height)
        base = base - hole

part = base
part.name = "hollow_box_with_holes"
export_step(part, "output.step")