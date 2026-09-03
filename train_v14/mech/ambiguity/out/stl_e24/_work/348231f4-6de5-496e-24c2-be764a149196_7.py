from build123d import *

with BuildPart() as p:
    Box(80, 30, 3)
    with Locations((0, 0, 1.5)):
        CounterBoreHole(2, 1, 2)

part = p.part
part.name = "box_with_cbore_hole"
export_step(part, "output.step")