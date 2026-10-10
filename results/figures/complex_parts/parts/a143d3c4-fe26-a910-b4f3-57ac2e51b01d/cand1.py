from build123d import *
import math

top_diameter = 80.0
bottom_diameter = 30.0
body_height = 40.0
boss_diameter = 20.0
boss_height = 12.0
hole_diameter = 5.0
hole_depth = 28.0
hole_count = 6
hole_radius = 30.0
chamfer_size = 2.0
slot_width = 10.0
slot_length = 20.0
slot_depth = 5.0

with BuildPart() as p:
    with BuildSketch() as s1:
        Circle(bottom_diameter / 2)
    with BuildSketch(Plane.XY.offset(body_height)) as s2:
        Circle(top_diameter / 2)
    loft()

solid_body = p.part
solid_body = solid_body + Pos(0, 0, boss_height / 2) * Cylinder(boss_diameter / 2, boss_height)

for i in range(hole_count):
    angle = math.radians(i * 360.0 / hole_count)
    px = hole_radius * math.cos(angle)
    py = hole_radius * math.sin(angle)
    solid_body = solid_body - Pos(px, py, body_height - hole_depth / 2) * Cylinder(hole_diameter / 2, hole_depth)

slot_box = Pos(boss_diameter / 2 + slot_depth / 2, 0, 0) * Box(slot_depth, slot_width, slot_length)
solid_body = solid_body - slot_box

top_edges = solid_body.edges().sort_by(Axis.Z)[-1:]
solid_body = chamfer(top_edges, chamfer_size)

part = solid_body
part.name = "tapered_body_with_boss"
export_step(part, "output.step")