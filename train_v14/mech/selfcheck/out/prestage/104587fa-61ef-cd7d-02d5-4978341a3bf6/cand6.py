from build123d import *
import math

outer_diameter = 80.0
thickness = 5.0
central_hole_diameter = 10.0
boss_diameter = 20.0
boss_height = 2.0
tab_width = 15.0
tab_height = 5.0
tab_thickness = 3.0
chamfer_size = 0.5
pattern_hole_diameter = 4.0
pattern_hole_count = 12
pattern_radius = 30.0
pocket_diameter = 30.0
pocket_depth = 2.0

with BuildPart() as p:
    with BuildSketch() as s:
        Circle(outer_diameter / 2)
        Circle(central_hole_diameter / 2, mode=Mode.SUBTRACT)
    extrude(amount=thickness)

solid_body = p.part
solid_body = chamfer(solid_body.edges(), chamfer_size)

solid_body = solid_body + Pos(0, 0, boss_height / 2) * Cylinder(boss_diameter / 2, boss_height)

tab_x = outer_diameter / 2 - tab_width / 2
solid_body = solid_body + Pos(tab_x, 0, tab_thickness / 2) * Box(tab_width, tab_height, tab_thickness)

for i in range(pattern_hole_count):
    angle = math.radians(i * 360.0 / pattern_hole_count)
    px = pattern_radius * math.cos(angle)
    py = pattern_radius * math.sin(angle)
    solid_body = solid_body - Pos(px, py, thickness / 2) * Cylinder(pattern_hole_diameter / 2, thickness)

solid_body = solid_body - Pos(0, 0, thickness - pocket_depth / 2) * Cylinder(pocket_diameter / 2, pocket_depth)

part = solid_body
part.name = "washer_with_boss_and_tabs"
export_step(part, "output.step")