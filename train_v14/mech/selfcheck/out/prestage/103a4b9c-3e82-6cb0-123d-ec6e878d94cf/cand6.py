from build123d import *

block_length = 70.0
block_width = 30.0
block_height = 20.0
pocket_length = 40.0
pocket_width = 15.0
pocket_depth = 6.0
tab_length = 10.0
tab_width = 8.0
tab_height = 5.0
slot_width = 3.0
slot_height = 8.0
slot_depth = 5.0
hole_diameter = 4.0
hole_spacing = 30.0
chamfer_size = 0.8
fillet_radius = 0.5

result = Box(block_length, block_width, block_height)
result = chamfer(result.edges().filter_by(Axis.Z), chamfer_size)

pocket = Pos(0, 0, -block_height/2 + pocket_depth/2) * Box(pocket_length, pocket_width, pocket_depth)
result = result - pocket

tab = Pos(block_length/2 + tab_height/2, 0, 0) * Box(tab_height, tab_width, tab_length)
result = result + tab

slot = Pos(block_length/2 + tab_height - slot_depth/2, 0, tab_length/2 - slot_height/2) * Box(slot_depth, slot_width, slot_height)
result = result - slot

for y in [-hole_spacing, 0, hole_spacing]:
    result = result - Pos(0, y, 0) * Cylinder(hole_diameter/2, block_height + 10)

result = fillet(result.edges().filter_by(Axis.Z), fillet_radius)

part = result
part.name = "block_with_pocket_tab_and_holes"
export_step(part, "output.step")