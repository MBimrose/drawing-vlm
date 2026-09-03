from build123d import *

block_length = 80.0
block_width = 40.0
block_height = 15.0
tab_length = 20.0
tab_width = 10.0
hole_diameter = 8.0
hole_spacing_x = 30.0
hole_spacing_y = 30.0
chamfer_size = 3.0
rib_thickness = 2.0
rib_height = 5.0
rib_length = block_length - 20.0

base = Box(block_length, block_width, block_height)
tab = Pos(block_length/2 + tab_length/2, 0, 0) * Box(tab_length, tab_width, block_height)
combined = base + tab

combined = chamfer(combined.edges().filter_by(Axis.Z), chamfer_size)

hole_positions = [
    (-hole_spacing_x/2, -hole_spacing_y/2),
    (hole_spacing_x/2, -hole_spacing_y/2),
    (-hole_spacing_x/2, hole_spacing_y/2),
    (hole_spacing_x/2, hole_spacing_y/2),
]
for x, y in hole_positions:
    combined = combined - Pos(x, y, 0) * Cylinder(hole_diameter/2, block_height * 2)

rib = Pos(0, 0, block_height/2) * Box(rib_length, rib_thickness, rib_height)
part = combined + rib
part.name = "block_with_tab_holes_and_rib"
export_step(part, "output.step")