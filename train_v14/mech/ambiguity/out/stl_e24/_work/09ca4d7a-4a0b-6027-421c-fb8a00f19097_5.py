from build123d import *
import math

hex_radius = 40
plate_thickness = 5
boss_diameter = 20
boss_height = 10
hole_diameter = 4.5
hole_pattern_radius = 20
chamfer_size = 0.5

with BuildPart() as p:
    with BuildSketch() as s:
        RegularPolygon(hex_radius, 6)
    extrude(amount=plate_thickness)

solid_body = p.part
solid_body = solid_body + Pos(0, 0, plate_thickness + boss_height/2) * Cylinder(boss_diameter/2, boss_height)

for i in range(6):
    angle = math.radians(i * 60)
    px = hole_pattern_radius * math.cos(angle)
    py = hole_pattern_radius * math.sin(angle)
    solid_body = solid_body - Pos(px, py, plate_thickness/2) * Cylinder(hole_diameter/2, plate_thickness + 1)

vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = chamfer(vertical_edges, chamfer_size)

part = solid_body
part.name = "hex_plate_with_boss"
export_step(part, "output.step")