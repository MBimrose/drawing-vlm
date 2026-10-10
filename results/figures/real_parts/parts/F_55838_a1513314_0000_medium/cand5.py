from build123d import *

shaft_diameter = 34.8
shaft_length = 60.0
boss_height = 20.0
boss_diameter = 53.3

shaft = Pos(shaft_length/2, 0, 0) * Rot(0, 90, 0) * Cylinder(shaft_diameter/2, shaft_length)

with BuildPart() as p:
    with BuildSketch(Plane.YZ) as s:
        RegularPolygon(boss_diameter/2, 6)
    extrude(amount=boss_height)
boss = p.part

part = shaft + boss
part.name = "shaft_with_hex_boss"
export_step(part, "output.step")