from build123d import *

block_length = 80.0
block_width = 40.0
block_height = 20.0
tab_length = 20.0
tab_width = 10.0
wall_thickness = 3.0
hole_diameter = 8.0
hole_spacing = 30.0
rib_height = 2.0
rib_thickness = 2.0
rib_spacing = 10.0
pocket_depth = 5.0
pocket_width = 20.0
pocket_length = 30.0

base = Box(block_length, block_width, block_height)
tab = Pos(block_length/2 + tab_length/2, 0, 0) * Box(tab_length, tab_width, block_height)
solid_body = base + tab
solid_body = offset(solid_body, amount=-wall_thickness)

hole_positions = [
    (-hole_spacing/2, -hole_spacing/2),
    ( hole_spacing/2, -hole_spacing/2),
    (-hole_spacing/2,  hole_spacing/2),
    ( hole_spacing/2,  hole_spacing/2)
]
for x, y in hole_positions:
    solid_body = solid_body - Pos(x, y, 0) * Cylinder(hole_diameter/2, block_height + 10)

rib_count = int((block_length - 2*wall_thickness) // rib_spacing)
for i in range(rib_count):
    x = -block_length/2 + wall_thickness + rib_spacing/2 + i * rib_spacing
    rib = Pos(x, 0, block_height/2 + rib_height/2) * Box(block_width - 2*wall_thickness, rib_thickness, rib_height)
    solid_body = solid_body + rib

pocket = Pos(0, 0, block_height/2 + rib_height - pocket_depth/2) * Box(pocket_length, pocket_width, pocket_depth)
solid_body = solid_body - pocket

part = solid_body
part.name = "hollow_block_with_tabs_ribs_pocket"
export_step(part, "output.step")