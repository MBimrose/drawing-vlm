from build123d import *

with BuildPart() as p:
    Box(50, 50, 8)
    top_face = p.part.faces().sort_by(Axis.Z)[-1]
    with Locations(top_face):
        CounterSinkHole(6, 4, 82)
    top_face = p.part.faces().sort_by(Axis.Z)[-1]
    chamfer(top_face.edges(), 2)

part = p.part
part.name = "box_with_countersink_and_chamfer"
export_step(part, "output.step")