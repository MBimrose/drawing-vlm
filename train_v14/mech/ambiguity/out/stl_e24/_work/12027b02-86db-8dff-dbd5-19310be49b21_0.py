from build123d import *

block_length = 80.0
block_width = 40.0
block_height = 20.0
tab_length = 20.0
tab_width = 15.0
wall_thickness = 2.5
hole_diameter = 8.0
hole_spacing_x = 30.0
hole_spacing_y = 30.0
rib_height = 5.0
rib_thickness = 2.0

base = Box(block_length, block_width, block_height)
tab = Pos(block_length/2 + tab_length/2, 0, 0) * Box(tab_length, tab_width, block_height)
combined = base + tab
hollow = offset(combined, amount=-wall_thickness)

rib = Pos(0, 0, block_height/2 - wall_thickness + rib_height/2) * Box(block_length - 2*wall_thickness, rib_thickness, rib_height)
with_rib = hollow + rib

hole_positions = [
    (-hole_spacing_x/2, -hole_spacing_y/2),
    ( hole_spacing_x/2, -hole_spacing_y/2),
    (-hole_spacing_x/2,  hole_spacing_y/2),
    ( hole_spacing_x/2,  hole_spacing_y/2),
]

result = with_rib
for x, y in hole_positions:
    result = result - Pos(x, y, 0) * Cylinder(hole_diameter/2, block_height + 10)

part = result
part.name = "hollow_block_with_tab_rib_holes"
export_step(part, "output.step")