from build123d import *

solid = Box(80, 60, 5)
solid = solid - Pos(0, 0, 1.5) * Cylinder(3, 2)
part = solid
part.name = "box_with_hole"
export_step(part, "output.step")