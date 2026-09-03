from build123d import *

with BuildPart() as p:
    Box(80, 30, 3)
    with Locations(Pos(0, 0, 1.5)):
        CounterSinkHole(2, 1, 2, 90)

part = p.part
part.name = "plate_with_countersink_hole"
export_step(part, "output.step")