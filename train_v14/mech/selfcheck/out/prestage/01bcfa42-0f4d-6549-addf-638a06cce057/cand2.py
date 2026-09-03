from build123d import *

base = Box(80, 60, 5)
hole = Pos(0, 0, 1.5) * Cylinder(3, 2)
part = base - hole
part.name = "plate_with_blind_hole"
export_step(part, "output.step")