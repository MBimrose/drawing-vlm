from build123d import *

block_length = 70.0
block_width = 30.0
block_height = 20.0
tab_length = 10.0
tab_width = 8.0
tab_height = 12.0
pocket_length = 40.0
pocket_width = 15.0
pocket_depth = 5.0
chamfer_size = 0.8
fillet_radius = 0.5
hole_diameter = 4.0
hole_spacing = 30.0
hole_offset_y = -block_width/2 + 5.0
rib_thickness = 2.0
rib_height = 5.0
rib_spacing = 12.0
rib_count = int((block_length - 20) // rib_spacing)

base = Pos(0, 0, block_height/2) * Box(block_length, block_width, block_height)
tab = Pos(block_length/2, 0, block_height/2 + tab_height/2) * Box(tab_length, tab_width, tab_height)
result = base + tab

result = chamfer(result.edges().filter_by(Axis.Z), chamfer_size)
result = fillet(result.edges().filter_by(Axis.Z), fillet_radius)

pocket = Pos(0, 0, pocket_depth/2) * Box(pocket_length, pocket_width, pocket_depth)
result = result - pocket

tab_pocket = Pos(block_length/2 + tab_length/2 - 1.0, 0, block_height/2 + tab_height/2) * Box(2.0, tab_width - 2.0, tab_height - 2.0)
result = result - tab_pocket

hole_positions = [(0, 0), (-hole_spacing/2, hole_offset_y), (hole_spacing/2, hole_offset_y)]
for x, y in hole_positions:
    result = result - Pos(x, y, block_height/2) * Cylinder(hole_diameter/2, block_height + 20)

for i in range(rib_count):
    x_pos = -block_length/2 + 10 + i * rib_spacing
    rib = Pos(x_pos, 0, block_height - rib_height/2) * Box(rib_thickness, rib_height, rib_height)
    result = result + rib

part = result
part.name = "block_with_tab_pockets_holes_ribs"
export_step(part, "output.step")