from build123d import *

with BuildPart() as p:
    Box(20, 20, 10)
    top_face = p.part.faces().sort_by(Axis.Z)[-1]
    with Locations(top_face):
        CounterSinkHole(2.5, 1.0, counter_sink_angle=82)

part = p.part
part.name = "box_with_countersink_hole"
export_step(part, "output.step")