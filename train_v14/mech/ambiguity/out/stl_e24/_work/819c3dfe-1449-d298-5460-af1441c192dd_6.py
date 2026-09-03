from build123d import *

base = Box(70, 30, 8)
hole1 = Pos(-20, 0, 0) * Cylinder(2, 8)
hole2 = Pos(20, 0, 0) * Cylinder(2, 8)
part = base - hole1 - hole2
part.name = "rectangular_block_with_holes"
export_step(part, "output.step")