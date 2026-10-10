from build123d import *
import math

outer_diameter = 60.0
thickness = 10.0
boss_diameter = 20.0
boss_height = 5.0
slot_width = 4.0
slot_length = 12.0
slot_count = 12
central_hole_diameter = 10.0
chamfer_size = 0.5

base = Pos(0, 0, thickness/2) * Cylinder(outer_diameter/2, thickness)
boss = Pos(0, 0, thickness + boss_height/2) * Cylinder(boss_diameter/2, boss_height)
result = base + boss

slot_radius = boss_diameter/2 + slot_length/2
for i in range(slot_count):
    angle = math.radians(i * 360.0 / slot_count)
    px = slot_radius * math.cos(angle)
    py = slot_radius * math.sin(angle)
    slot = Pos(px, py, thickness + boss_height/2) * Rot(0, 0, math.degrees(angle)) * Box(slot_width, slot_length, boss_height)
    result = result - slot

result = result - Pos(0, 0, (thickness + boss_height)/2) * Cylinder(central_hole_diameter/2, thickness + boss_height + 1)

result = chamfer(result.edges().filter_by(Axis.Z), chamfer_size)

part = result
part.name = "flanged_disc_with_slots"
export_step(part, "output.step")