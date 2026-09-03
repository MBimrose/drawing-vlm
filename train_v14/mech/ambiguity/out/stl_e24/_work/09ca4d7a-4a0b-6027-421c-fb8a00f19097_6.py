from build123d import *
import math

hex_radius = 40.0
base_thickness = 5.0
boss_diameter = 20.0
boss_height = 10.0
hole_diameter = 4.5
hole_pattern_radius = 20.0
chamfer_size = 0.8

with BuildPart() as p:
    with BuildSketch() as s:
        RegularPolygon(hex_radius, 6)
    extrude(amount=base_thickness)

solid_body = p.part
solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_size)

boss = Pos(0, 0, base_thickness + boss_height/2) * Cylinder(boss_diameter/2, boss_height)
solid_body = solid_body + boss

for i in range(6):
    angle = math.radians(i * 60)
    px = hole_pattern_radius * math.cos(angle)
    py = hole_pattern_radius * math.sin(angle)
    hole = Pos(px, py, base_thickness + boss_height/2) * Cylinder(hole_diameter/2, base_thickness + boss_height + 10)
    solid_body = solid_body - hole

part = solid_body
part.name = "hex_base_with_boss_and_holes"
export_step(part, "output.step")