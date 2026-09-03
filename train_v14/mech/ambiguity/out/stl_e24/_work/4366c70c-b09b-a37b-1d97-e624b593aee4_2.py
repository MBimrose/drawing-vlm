from build123d import *
import math

outer_diameter = 80.0
thickness = 10.0
central_hole_diameter = 20.0
slot_width = 6.0
slot_length = 20.0
slot_offset_radius = 30.0
chamfer_distance = 1.0
rib_width = 4.0
rib_length = 15.0
rib_height = 2.0
rib_offset_radius = 25.0

result = Cylinder(outer_diameter / 2, thickness)
result = result - Cylinder(central_hole_diameter / 2, thickness)

for i in range(4):
    angle = math.radians(i * 90)
    x = slot_offset_radius * math.cos(angle)
    y = slot_offset_radius * math.sin(angle)
    result = result - Pos(x, y, 0) * Box(slot_width, slot_length, thickness)

result = chamfer(result.edges().filter_by(Axis.Z), chamfer_distance)

for i in range(4):
    angle = math.radians(i * 90)
    x = rib_offset_radius * math.cos(angle)
    y = rib_offset_radius * math.sin(angle)
    result = result + Pos(x, y, 0) * Box(rib_width, rib_length, rib_height)

part = result
part.name = "flanged_disk_with_slots_and_ribs"
export_step(part, "output.step")