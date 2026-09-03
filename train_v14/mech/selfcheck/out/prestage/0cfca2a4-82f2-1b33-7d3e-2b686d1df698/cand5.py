from build123d import *

length = 80.0
width = 25.0
thickness = 5.0
spline_depth = 10.0
hole_diameter = 4.0
hole_spacing = 30.0
chamfer_size = 0.5

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            l1 = Line((0, 0), (length, 0))
            l2 = Line(l1 @ 1, (length, width))
            l3 = Line(l2 @ 1, (0, width))
            Spline((0, width), (-spline_depth/2, width/2), (0, 0))
        make_face()
    extrude(amount=thickness)

solid_body = p.part

for x, y in [(length/2, width/2 - hole_spacing/2), (length/2, width/2 + hole_spacing/2)]:
    solid_body = solid_body - Pos(x, y, thickness/2) * Cylinder(hole_diameter/2, thickness * 2)

x_face = solid_body.faces().sort_by(Axis.X)[-1]
solid_body = chamfer(x_face.edges(), chamfer_size)

part = solid_body
part.name = "spline_plate"
export_step(part, "output.step")