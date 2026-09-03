from build123d import *

length = 80.0
width = 25.0
thickness = 5.0
notch_radius = 8.0
chamfer_size = 0.5

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            l1 = Line((0, 0), (length, 0))
            l2 = Line(l1 @ 1, (length, width))
            l3 = Line(l2 @ 1, (0, width))
            ThreePointArc(l3 @ 1, (-notch_radius, width/2), (0, 0))
        make_face()
    extrude(amount=thickness)

solid_body = p.part
x_face = solid_body.faces().sort_by(Axis.X)[-1]
solid_body = chamfer(x_face.edges(), chamfer_size)

part = solid_body
part.name = "notched_plate"
export_step(part, "output.step")