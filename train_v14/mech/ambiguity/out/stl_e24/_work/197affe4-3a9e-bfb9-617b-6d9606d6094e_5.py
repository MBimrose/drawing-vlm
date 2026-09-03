from build123d import *

block_length = 80.0
block_width = 50.0
block_height = 30.0
pocket_length = 40.0
pocket_width = 30.0
pocket_depth = 10.0
rib_thickness = 4.0
rib_height = 12.0
hole_diameter = 5.0
hole_spacing = 35.0
chamfer_size = 0.5

base = Box(block_length, block_width, block_height)
rib_top = Pos(0, 0, block_height/2 - rib_height/2) * Box(block_length, rib_thickness, rib_height)
rib_bottom = Pos(0, 0, -block_height/2 + rib_height/2) * Box(block_length, rib_thickness, rib_height)
result = base + rib_top + rib_bottom

pocket = Pos(0, 0, block_height/2 - pocket_depth/2) * Box(pocket_length, pocket_width, pocket_depth)
result = result - pocket

for x in [-hole_spacing/2, hole_spacing/2]:
    hole = Pos(x, 0, 0) * Rot(90, 0, 0) * Cylinder(hole_diameter/2, block_width + 20)
    result = result - hole

result = chamfer(result.edges().filter_by(Axis.Z), chamfer_size)

part = result
part.name = "ribbed_block_with_pocket"
export_step(part, "output.step")