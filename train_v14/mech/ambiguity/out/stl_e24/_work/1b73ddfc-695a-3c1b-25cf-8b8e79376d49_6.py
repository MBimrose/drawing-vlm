from build123d import *

with BuildPart() as p:
    Box(60, 40, 8)
    CounterSinkHole(2, 2.5, 4, 82)

part = p.part
part.name = "box_with_countersink_hole"
export_step(part, "output.step")