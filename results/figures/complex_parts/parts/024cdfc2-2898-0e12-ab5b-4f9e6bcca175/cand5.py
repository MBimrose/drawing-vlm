from build123d import *
import math

outer_radius = 30.0
inner_radius = 12.0
knob_height = 20.0
wall_thickness = outer_radius - inner_radius
slot_width = 6.0
slot_length = 12.0
slot_offset_from_top = 5.0
fillet_radius = 2.0
rib_thickness = 2.0
rib_height = 8.0
rib_count = 6
boss_radius = 5.0
boss_height = 5.0

result = Pos(0, 0, knob_height/2) * Cylinder(outer_radius, knob_height)
result = result - Pos(0, 0, knob_height/2) * Cylinder(inner_radius, knob_height)
result = fillet(result.edges(), fillet_radius)

slot_center_z = knob_height - slot_offset_from_top - slot_length/2
slot_box = Pos(outer_radius - wall_thickness/2, 0, slot_center_z) * Box(slot_width, wall_thickness, slot_length)
result = result - slot_box

for i in range(rib_count):
    angle = i * 360.0 / rib_count
    rib = Rot(0, 0, angle) * Pos(inner_radius + rib_thickness/2, 0, 0) * Box(rib_thickness, rib_height, knob_height)
    result = result + rib

boss = Pos(outer_radius - boss_radius/2, 0, boss_height/2) * Cylinder(boss_radius, boss_height)
result = result + boss

part = result
part.name = "knob_with_ribs_and_boss"
export_step(part, "output.step")