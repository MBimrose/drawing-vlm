from build123d import *

cyl = Pos(40, 0, 0) * Rot(0, 90, 0) * Cylinder(17.4, 80)
with BuildPart() as p:
    with BuildSketch(Plane.YZ) as s:
        RegularPolygon(30, 6)
    extrude(amount=20)
hex_solid = p.part
part = cyl + hex_solid
part.name = "cyl_with_hex"
export_step(part, "output.step")