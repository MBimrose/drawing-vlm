from build123d import *

base = Box(70, 30, 8)
for x in [-20, 20]:
    base = base - Pos(x, 0, 0) * Cylinder(2, 16)

part = base
part.name = "box_with_holes"
export_step(part, "output.step")