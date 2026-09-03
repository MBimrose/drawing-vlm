from build123d import *

block_length = 60.0
block_width = 40.0
block_height = 20.0
fillet_radius = 3.0
pocket_length = 50.0
pocket_width = 30.0
pocket_depth = 8.0
hole_diameter = 5.0
hole_spacing_x = 20.0
hole_spacing_y = 15.0
hole_rows = 2
hole_cols = 2
rib_width = 8.0
rib_length = 50.0
rib_height = 2.0
countersink_diameter = 6.0
countersink_depth = 2.0
countersink_angle = 45.0
side_hole_diameter = 4.0
side_hole_spacing = 15.0
side_hole_offset = 10.0

result = Box(block_length, block_width, block_height)
result = fillet(result.edges(), fillet_radius)

pocket = Pos(0, 0, block_height/2 - pocket_depth/2) * Box(pocket_length, pocket_width, pocket_depth)
result = result - pocket

for i in range(hole_cols):
    for j in range(hole_rows):
        x = (i - (hole_cols-1)/2) * hole_spacing_x
        y = (j - (hole_rows-1)/2) * hole_spacing_y
        result = result - Pos(x, y, 0) * Cylinder(hole_diameter/2, block_height + 10)

rib = Pos(0, 0, block_height/2 + rib_height/2) * Box(rib_width, rib_length, rib_height)
result = result + rib

for i in range(2):
    y = side_hole_offset + (i - 0.5) * side_hole_spacing
    result = result - Pos(block_length/2, y, 0) * Rot(0, 90, 0) * CounterSinkHole(side_hole_diameter/2, countersink_diameter/2, countersink_depth, countersink_angle)

part = result
part.name = "block_with_pocket_holes_rib"
export_step(part, "output.step")