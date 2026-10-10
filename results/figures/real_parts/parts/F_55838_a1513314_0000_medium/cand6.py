from build123d import *

hex_radius = 35.0
flange_thickness = 20.0
boss_radius = 17.4
boss_height = 60.0
overlap = 0.5

with BuildPart() as p:
    with BuildSketch(Plane.YZ) as s1:
        RegularPolygon(hex_radius, 6)
    extrude(amount=flange_thickness)
    with BuildSketch(Plane.YZ.offset(flange_thickness - overlap)) as s2:
        Circle(boss_radius)
    extrude(amount=boss_height)

part = p.part
part.name = "hex_flange_with_boss"
export_step(part, "output.step")