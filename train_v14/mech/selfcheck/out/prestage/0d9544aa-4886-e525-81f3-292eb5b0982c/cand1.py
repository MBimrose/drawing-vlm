from build123d import *

with BuildPart() as p:
    Box(20, 20, 10)
    with Locations((0, 0, 2.5)):
        CounterSinkHole(2.5, 2.5, 5, 90)

part = p.part
part.name = "box_with_csk_hole"
export_step(part, "output.step")