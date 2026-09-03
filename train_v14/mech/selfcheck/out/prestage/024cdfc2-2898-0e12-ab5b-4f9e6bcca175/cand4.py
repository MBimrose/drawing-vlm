from build123d import *
import math

outer_radius = 30.0
inner_radius = 12.0
height = 20.0
fillet_radius = 2.0
slot_width = 6.0
slot_depth = 8.0
boss_radius = 5.0
boss_height = 4.0
rib_thickness = 2.0
rib_height = 8.0
rib_count = 6

result = Pos(0, 0, height/2) * Cylinder(outer_radius, height)
result = result - Pos(0, 0, height/2) * Cylinder(inner_radius, height)
result = fillet(result.edges(), fillet_radius)

slot_box = Pos(outer_radius - slot_depth/2, 0, height/2) * Box(slot_depth, slot_width, height)
result = result - slot_box

boss = Pos(outer_radius - boss_height/2, 0, 0) * Cylinder(boss_radius, boss_height)
result = result + boss

rib = Pos(inner_radius + rib_thickness/2, 0, 0) * Box(rib_thickness, rib_height, height)
for i in range(rib_count):
    angle = i * 360.0 / rib_count
    result = result + Rot(0, 0, angle) * rib

part = result
part.name = "hollow_cylinder_with_ribs"
export_step(part, "output.step")