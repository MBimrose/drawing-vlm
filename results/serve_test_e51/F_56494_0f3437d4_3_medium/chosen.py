from build123d import *

hex_radius = 40
hex_height = 24
hole_radius = 12

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as s:
        RegularPolygon(hex_radius, 6)
    extrude(amount=hex_height)

solid_body = p.part
hole = Rot(90, 0, 0) * Cylinder(hole_radius, hex_height * 2)
solid_body = solid_body - hole

part = solid_body
part.name = "hex_prism_with_hole"
export_step(part, "output.step")