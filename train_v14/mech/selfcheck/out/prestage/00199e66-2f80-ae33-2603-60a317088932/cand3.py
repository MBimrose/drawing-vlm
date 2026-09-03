from build123d import *

block_length = 80.0
block_width = 60.0
block_thickness = 12.0
pocket_diameter = 30.0
pocket_depth = 6.0
countersink_hole_diameter = 5.0
countersink_diameter = 10.0
countersink_angle = 82.0
hole_offset = 15.0
chamfer_size = 1.0

solid_body = Box(block_length, block_width, block_thickness)
solid_body = solid_body - Pos(0, 0, block_thickness/2 - pocket_depth/2) * Cylinder(pocket_diameter/2, pocket_depth)

hole_positions = [
    (-block_length/2 + hole_offset, -block_width/2 + hole_offset),
    (block_length/2 - hole_offset, -block_width/2 + hole_offset),
    (-block_length/2 + hole_offset, block_width/2 - hole_offset),
    (block_length/2 - hole_offset, block_width/2 - hole_offset),
]

for x, y in hole_positions:
    solid_body = solid_body - Pos(x, y, block_thickness/2) * CounterSinkHole(countersink_hole_diameter/2, countersink_diameter/2, block_thickness, countersink_angle)

solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_size)

part = solid_body
part.name = "block_with_pocket_and_holes"
export_step(part, "output.step")