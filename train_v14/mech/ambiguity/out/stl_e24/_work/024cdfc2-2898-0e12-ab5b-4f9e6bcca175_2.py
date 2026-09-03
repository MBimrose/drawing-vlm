from build123d import *
import math

outer_radius = 30.0
inner_radius = 12.0
height = 20.0
fillet_radius = 2.0
rib_thickness = 2.0
rib_height = 6.0
rib_spacing_angle = 30.0
slot_width = 6.0
slot_length = 12.0
slot_depth = 8.0
boss_radius = 5.0
boss_height = 4.0

result = Pos(0, 0, height/2) * Cylinder(outer_radius, height)
result = result - Pos(0, 0, height/2) * Cylinder(inner_radius, height)
result = fillet(result.edges(), fillet_radius)

num_ribs = int(360 / rib_spacing_angle)
for i in range(num_ribs):
    angle = i * rib_spacing_angle
    rib = Rot(0, 0, angle) * Pos(inner_radius + rib_thickness/2, 0, 0) * Box(rib_thickness, rib_height, height)
    result = result + rib

slot = Pos(outer_radius - slot_depth/2, 0, height/2) * Box(slot_depth, slot_width, slot_length)
result = result - slot

boss = Pos(outer_radius - boss_radius, 0, 0) * Cylinder(boss_radius, boss_height)
result = result + boss

part = result
part.name = "hollow_cylinder_with_ribs"
export_step(part, "output.step")