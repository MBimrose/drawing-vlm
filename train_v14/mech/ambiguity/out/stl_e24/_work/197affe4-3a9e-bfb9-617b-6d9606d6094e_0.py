from build123d import *

block_length = 80.0
block_width = 50.0
block_height = 30.0
pocket_length = 40.0
pocket_width = 30.0
pocket_depth = 15.0
rib_thickness = 5.0
rib_height = 20.0
chamfer_size = 1.0
hole_diameter = 5.0
hole_spacing = 35.0

base = Box(block_length, block_width, block_height)
rib1 = Box(block_length, rib_thickness, rib_height)
rib2 = Box(rib_thickness, block_width, rib_height)
combined = base + rib1 + rib2

pocket = Pos(0, 0, block_height/2 - pocket_depth/2) * Box(pocket_length, pocket_width, pocket_depth)
pocket = chamfer(pocket.edges().filter_by(Axis.Z), chamfer_size)
result = combined - pocket

hole1 = Pos(-hole_spacing/2, 0, 0) * Rot(90, 0, 0) * Cylinder(hole_diameter/2, block_width + 10)
hole2 = Pos(hole_spacing/2, 0, 0) * Rot(90, 0, 0) * Cylinder(hole_diameter/2, block_width + 10)
result = result - hole1 - hole2

part = result
part.name = "ribbed_block_with_pocket"
export_step(part, "output.step")