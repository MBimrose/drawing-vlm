from build123d import *

with BuildPart() as p:
    Box(80, 30, 3)
    with Locations((0, 0, 1.5)):
        CounterSinkHole(2, 1, counter_sink_angle=82)

part = p.part
part.name = "box_with_countersink_hole"
export_step(part, "output.step")