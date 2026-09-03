from build123d import *
import math

outer_diameter = 80.0
thickness = 10.0
central_hole_diameter = 20.0
slot_width = 6.0
slot_length = 20.0
slot_offset_radius = 30.0
chamfer_distance = 1.0
mount_hole_diameter = 5.0
mount_hole_offset = 30.0
boss_diameter = 30.0
boss_height = 4.0

base = Cylinder(outer_diameter / 2, thickness)
boss = Cylinder(boss_diameter / 2, boss_height)
result = base + boss

result = result - Cylinder(central_hole_diameter / 2, thickness + 2)

for i in range(4):
    angle = math.radians(i * 90)
    px = slot_offset_radius * math.cos(angle)
    py = slot_offset_radius * math.sin(angle)
    result = result - Pos(px, py, 0) * Box(slot_width, slot_length, thickness + 2)

for i in range(4):
    angle = math.radians(i * 90)
    px = mount_hole_offset * math.cos(angle)
    py = mount_hole_offset * math.sin(angle)
    result = result - Pos(px, py, 0) * Cylinder(mount_hole_diameter / 2, thickness + 2)

result = chamfer(result.edges().filter_by(Axis.Z), chamfer_distance)

part = result
part.name = "flanged_disc_with_slots"
export_step(part, "output.step")