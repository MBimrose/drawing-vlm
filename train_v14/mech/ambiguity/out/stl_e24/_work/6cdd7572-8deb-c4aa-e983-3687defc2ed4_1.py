from build123d import *

base = Box(40, 12, 4)
hole = Pos(10, 0, 0) * Cylinder(1.65, 4)
slot = Pos(-10, 3, 0) * Box(2, 6, 4)
part = base - hole - slot
part.name = "plate_with_hole_and_slot"
export_step(part, "output.step")