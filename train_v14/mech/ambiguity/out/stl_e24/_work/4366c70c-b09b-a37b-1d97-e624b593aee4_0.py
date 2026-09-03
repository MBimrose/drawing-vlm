from build123d import *
import math

outer_diameter = 80.0
thickness = 10.0
central_hole_diameter = 20.0
slot_width = 6.0
slot_length = 20.0
slot_offset = 12.0
chamfer_distance = 1.0
hub_diameter = 30.0
hub_height = 6.0

base = Cylinder(outer_diameter / 2, thickness)
hub = Cylinder(hub_diameter / 2, hub_height)
result = base + hub

result = result - Cylinder(central_hole_diameter / 2, thickness + 1)

slot_center_radius = central_hole_diameter / 2 + slot_offset
for i in range(4):
    angle = math.radians(i * 90)
    x = slot_center_radius * math.cos(angle)
    y = slot_center_radius * math.sin(angle)
    result = result - Pos(x, y, 0) * Box(slot_width, slot_length, thickness + 1)

result = chamfer(result.edges().filter_by(Axis.Z), chamfer_distance)

part = result
part.name = "flanged_disc_with_slots"
export_step(part, "output.step")