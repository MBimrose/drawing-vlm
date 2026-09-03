from build123d import *
import math

outer_radius = 30
inner_radius = 12
wall_thickness = outer_radius - inner_radius
length = 20
slot_width = 6
slot_depth = wall_thickness * 0.6
fillet_radius = 2
rib_count = 6
rib_thickness = 4
rib_height = 12
boss_radius = 5
boss_height = 5

result = Cylinder(outer_radius, length) - Cylinder(inner_radius, length)
result = fillet(result.edges(), fillet_radius)

slot_box = Pos(outer_radius - slot_depth / 2, 0, 0) * Box(slot_depth, slot_width, length)
result = result - slot_box

boss = Pos(outer_radius, 0, -length / 2) * Cylinder(boss_radius, boss_height)
result = result + boss

rib = Pos(inner_radius, 0, -length / 2) * Box(rib_thickness, rib_height, wall_thickness)
for i in range(rib_count):
    angle = i * 360 / rib_count
    result = result + Rot(0, 0, angle) * rib

part = result
part.name = "hollow_cylinder_with_ribs"
export_step(part, "output.step")