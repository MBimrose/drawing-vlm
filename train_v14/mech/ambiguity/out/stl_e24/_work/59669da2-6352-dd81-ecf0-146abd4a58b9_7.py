from build123d import *

leaf_length = 80.0
leaf_width = 30.0
leaf_thickness = 6.0
rib_height = 12.0
rib_width = 20.0
fillet_radius = 2.0
hole_diameter = 5.0
hole_spacing_x = 20.0
hole_spacing_y = 10.0
hole_rows = 2
hole_cols = 3
hole_offset_x = -leaf_length/2 + 20.0
hole_offset_y = -leaf_width/2 + 10.0

base = Box(leaf_length, leaf_width, leaf_thickness)
rib = Pos(leaf_length/2 - rib_width/2, 0, leaf_thickness) * Box(rib_width, leaf_width, rib_height)
result = base + rib

for i in range(hole_cols):
    for j in range(hole_rows):
        x = hole_offset_x + i * hole_spacing_x
        y = hole_offset_y + j * hole_spacing_y
        result = result - Pos(x, y, 0) * Cylinder(hole_diameter/2, 30)

result = fillet(result.edges(), fillet_radius)
part = result
part.name = "leaf_with_rib_and_holes"
export_step(part, "output.step")