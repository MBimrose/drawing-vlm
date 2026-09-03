from build123d import *

outer_width = 80.0
outer_height = 60.0
length = 100.0
groove_width = 30.0
groove_depth = 5.0
hole_diameter = 8.0
chamfer_size = 1.0

base = Box(outer_width, outer_height, length)
groove = Pos(0, outer_height/2 - groove_depth/2, 0) * Box(groove_width, groove_depth, length)
result = base - groove
result = result - Cylinder(hole_diameter/2, length)
result = chamfer(result.edges().filter_by(Axis.Z), chamfer_size)

part = result
part.name = "grooved_block_with_hole"
export_step(part, "output.step")