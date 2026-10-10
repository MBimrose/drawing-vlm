from build123d import *

cyl = Pos(40, 0, 0) * Rot(0, 90, 0) * Cylinder(17.4, 60)
with BuildPart() as p:
    with BuildSketch(Plane.YZ) as s:
        RegularPolygon(26.65, 6)
    extrude(amount=20)
hex_solid = p.part
part = cyl + hex_solid
part.name = "cylinder_with_hex_flange"
export_step(part, "output.step")