from build123d import *

cyl = Pos(30, 0, 0) * Rot(0, 90, 0) * Cylinder(17.4, 60)
with BuildPart() as p:
    with BuildSketch(Plane.YZ) as s:
        RegularPolygon(30.75, 6)
    extrude(amount=20)
hex_prism = p.part
part = cyl + hex_prism
part.name = "cylinder_with_hex_boss"
export_step(part, "output.step")