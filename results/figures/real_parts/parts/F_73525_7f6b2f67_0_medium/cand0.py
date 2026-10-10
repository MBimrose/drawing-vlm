from build123d import *
import math

outer_diameter = 80.0
thickness = 20.0
wall_thickness = 4.0
slot_width = 12.0
slot_depth = 6.0
fillet_radius = 2.0
mount_hole_dia = 5.0
boss_diameter = 15.0
boss_height = 8.0
rib_width = 6.0
rib_height = 10.0

outer_radius = outer_diameter / 2.0
inner_radius = outer_radius - wall_thickness

result = Rot(0, 90, 0) * Cylinder(outer_radius, thickness)
result = result - Rot(0, 90, 0) * Cylinder(inner_radius, thickness)

slot_box = Pos(outer_radius - slot_depth / 2.0, 0, 0) * Box(slot_depth, slot_width, thickness)
result = result - slot_box

result = fillet(result.edges(), fillet_radius)

for i in range(4):
    angle = math.radians(i * 90)
    px = (inner_radius - wall_thickness / 2.0) * math.cos(angle)
    py = (inner_radius - wall_thickness / 2.0) * math.sin(angle)
    hole = Pos(px, py, 0) * Rot(0, 90, 0) * Cylinder(mount_hole_dia / 2.0, wall_thickness + 0.2)
    result = result - hole

boss = Pos(outer_radius + boss_height / 2.0, 0, 0) * Rot(0, 90, 0) * Cylinder(boss_diameter / 2.0, boss_height)
result = result + boss

for i in range(4):
    angle = i * 90
    rib = Rot(angle, 0, 0) * Pos(inner_radius - rib_height / 2.0, 0, 0) * Box(rib_height, rib_width, thickness)
    result = result + rib

part = result
part.name = "hollow_cylinder_with_slot_ribs"
export_step(part, "output.step")