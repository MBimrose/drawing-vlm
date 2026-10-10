from build123d import *
import math

outer_diameter = 80.0
wall_thickness = 6.0
height = 50.0
boss_diameter = 30.0
boss_height = 12.0
slot_width = 8.0
slot_length = 30.0
slot_count = 12
chamfer_size = 2.0
rib_thickness = 2.0
rib_height = 12.0
rib_count = 12

outer_radius = outer_diameter / 2.0
inner_radius = outer_radius - wall_thickness
boss_radius = boss_diameter / 2.0

result = Cylinder(outer_radius, height)
result = result - Cylinder(inner_radius, height)
result = result + Cylinder(boss_radius, boss_height)

top_face = result.faces().sort_by(Axis.Z)[-1]
result = chamfer(top_face.edges(), chamfer_size)

slot_radius = outer_radius - wall_thickness / 2.0
for i in range(slot_count):
    angle = math.radians(i * 360.0 / slot_count)
    px = slot_radius * math.cos(angle)
    py = slot_radius * math.sin(angle)
    slot = Pos(px, py, height / 2.0) * Rot(0, 0, math.degrees(angle)) * Box(slot_width, slot_length, height)
    result = result - slot

rib_radius = inner_radius + rib_thickness / 2.0
for i in range(rib_count):
    angle = math.radians(i * 360.0 / rib_count)
    px = rib_radius * math.cos(angle)
    py = rib_radius * math.sin(angle)
    rib = Pos(px, py, height / 2.0) * Rot(0, 0, math.degrees(angle)) * Box(rib_thickness, rib_height, height)
    result = result + rib

part = result
part.name = "hollow_cylinder_with_slots_and_ribs"
export_step(part, "output.step")