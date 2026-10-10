from build123d import *
import math

base_diameter = 30.0
top_diameter = 80.0
height = 40.0
boss_diameter = 20.0
boss_height = 8.0
hole_diameter = 5.0
hole_count = 6
hole_circle_radius = 30.0
slot_width = 10.0
slot_height = 20.0
slot_offset = 15.0
chamfer_size = 1.0

with BuildPart() as p:
    with BuildSketch() as s1:
        Circle(base_diameter / 2)
    with BuildSketch(Plane.XY.offset(height)) as s2:
        Circle(top_diameter / 2)
    loft()

solid_body = p.part
solid_body = solid_body + Pos(0, 0, height + boss_height / 2) * Cylinder(boss_diameter / 2, boss_height)

for i in range(hole_count):
    angle = math.radians(i * 360.0 / hole_count)
    px = hole_circle_radius * math.cos(angle)
    py = hole_circle_radius * math.sin(angle)
    solid_body = solid_body - Pos(px, py, height + boss_height / 2) * Cylinder(hole_diameter / 2, height + boss_height + 20)

slot_box = Pos(base_diameter / 2, 0, slot_offset) * Box(base_diameter, slot_width, slot_height)
solid_body = solid_body - slot_box

vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = chamfer(vertical_edges, chamfer_size)

part = solid_body
part.name = "conical_loft_with_boss_holes_slot"
export_step(part, "output.step")