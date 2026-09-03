from build123d import *
import math

outer_diameter = 80.0
inner_diameter = 20.0
thickness = 10.0
slot_width = 5.0
slot_length = (outer_diameter - inner_diameter) / 2.0
slot_center_radius = inner_diameter / 2.0 + slot_length / 2.0
mount_hole_diameter = 5.0
mount_hole_offset = 30.0

with BuildPart() as p:
    with BuildSketch() as s:
        Circle(outer_diameter / 2.0)
    extrude(amount=thickness)

solid_body = p.part
solid_body = solid_body - Pos(0, 0, thickness / 2) * Cylinder(inner_diameter / 2.0, thickness)

for angle in [0, 180]:
    rad = math.radians(angle)
    x = slot_center_radius * math.cos(rad)
    y = slot_center_radius * math.sin(rad)
    solid_body = solid_body - Pos(x, y, thickness / 2) * Box(slot_length, slot_width, thickness)

for angle in [90, 270]:
    rad = math.radians(angle)
    x = mount_hole_offset * math.cos(rad)
    y = mount_hole_offset * math.sin(rad)
    solid_body = solid_body - Pos(x, y, thickness / 2) * Cylinder(mount_hole_diameter / 2.0, thickness)

part = solid_body
part.name = "flanged_disc_with_slots"
export_step(part, "output.step")