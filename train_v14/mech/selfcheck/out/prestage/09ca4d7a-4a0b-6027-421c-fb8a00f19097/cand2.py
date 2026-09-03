from build123d import *
import math

hex_radius = 40.0
plate_thickness = 5.0
boss_radius = 10.0
boss_height = 10.0
hole_diameter = 4.5
hole_circle_radius = 20.0
chamfer_distance = 1.0

with BuildPart() as p:
    with BuildSketch() as s:
        RegularPolygon(hex_radius, 6)
    extrude(amount=plate_thickness)

solid_body = p.part
solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_distance)

for i in range(6):
    angle = math.radians(i * 60)
    px = hole_circle_radius * math.cos(angle)
    py = hole_circle_radius * math.sin(angle)
    solid_body = solid_body - Pos(px, py, plate_thickness / 2) * Cylinder(hole_diameter / 2, plate_thickness + 2)

solid_body = solid_body + Pos(0, 0, plate_thickness + boss_height / 2) * Cylinder(boss_radius, boss_height)

part = solid_body
part.name = "hex_plate_with_boss"
export_step(part, "output.step")