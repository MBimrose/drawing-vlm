from build123d import *
import math

outer_diameter = 60.0
thickness = 10.0
boss_diameter = 15.0
boss_height = 5.0
central_hole_diameter = 10.0
slot_width = 2.0
slot_depth = 4.0
slot_count = 12
chamfer_size = 0.5

base = Pos(0, 0, thickness / 2) * Cylinder(outer_diameter / 2, thickness)
boss = Pos(0, 0, thickness + boss_height / 2) * Cylinder(boss_diameter / 2, boss_height)
result = base + boss

hole = Pos(0, 0, (thickness + boss_height) / 2) * Cylinder(central_hole_diameter / 2, thickness + boss_height)
result = result - hole

slot_radius = boss_diameter / 2 + slot_depth / 2
for i in range(slot_count):
    angle = math.radians(i * 360.0 / slot_count)
    px = slot_radius * math.cos(angle)
    py = slot_radius * math.sin(angle)
    slot = Pos(px, py, thickness + boss_height / 2) * Rot(0, 0, math.degrees(angle)) * Box(slot_width, slot_depth, boss_height)
    result = result - slot

vertical_edges = result.edges().filter_by(Axis.Z)
result = chamfer(vertical_edges, chamfer_size)

part = result
part.name = "flanged_disc_with_slots"
export_step(part, "output.step")