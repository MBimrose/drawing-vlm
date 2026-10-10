from build123d import *
import math

outer_radius = 30.0
inner_radius = 12.0
height = 20.0
fillet_radius = 2.0
slot_width = 6.0
slot_depth = 8.0
rib_count = 6
rib_thickness = 2.0
rib_height = 8.0
rib_length = outer_radius - inner_radius - 2.0
boss_radius = 5.0
boss_height = 5.0

result = Pos(0, 0, height/2) * Cylinder(outer_radius, height)
result = result - Pos(0, 0, height/2) * Cylinder(inner_radius, height)
result = fillet(result.edges(), fillet_radius)

slot_box = Pos(outer_radius - slot_depth/2, 0, height/2) * Box(slot_width, slot_depth, height)
result = result - slot_box

for i in range(rib_count):
    angle = i * 360.0 / rib_count
    rib = Rot(0, 0, angle) * Pos(inner_radius + rib_length/2, 0, 0) * Box(rib_thickness, rib_height, height)
    result = result + rib

boss = Pos(outer_radius - boss_radius, 0, boss_height/2) * Cylinder(boss_radius, boss_height)
result = result + boss

part = result
part.name = "cylindrical_part_with_ribs"
export_step(part, "output.step")