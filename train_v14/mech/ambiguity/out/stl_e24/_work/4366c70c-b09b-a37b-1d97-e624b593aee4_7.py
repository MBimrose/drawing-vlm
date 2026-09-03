from build123d import *
import math

outer_diameter = 80.0
inner_diameter = 20.0
thickness = 10.0
slot_width = 6.0
slot_length = 20.0
slot_offset = 2.0
chamfer_size = 1.0
rib_width = 3.0
rib_height = 2.0
rib_length = 12.0

outer_radius = outer_diameter / 2.0
inner_radius = inner_diameter / 2.0
slot_center_radius = inner_radius + slot_offset + slot_length / 2.0
rib_center_radius = inner_radius + rib_length / 2.0

result = Cylinder(outer_radius, thickness)
result = result - Cylinder(inner_radius, thickness)

for i in range(4):
    angle = math.radians(i * 90)
    px = slot_center_radius * math.cos(angle)
    py = slot_center_radius * math.sin(angle)
    result = result - Pos(px, py, 0) * Box(slot_width, slot_length, thickness)

result = chamfer(result.edges().filter_by(Axis.Z), chamfer_size)

for i in range(4):
    angle = math.radians(i * 90 + 45)
    px = rib_center_radius * math.cos(angle)
    py = rib_center_radius * math.sin(angle)
    result = result + Pos(px, py, rib_height / 2) * Box(rib_width, rib_length, rib_height)

part = result
part.name = "flanged_disc_with_slots_and_ribs"
export_step(part, "output.step")