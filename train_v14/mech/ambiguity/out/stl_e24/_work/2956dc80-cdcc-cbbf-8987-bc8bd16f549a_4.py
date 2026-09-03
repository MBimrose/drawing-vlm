from build123d import *
import math

outer_diameter = 80.0
inner_diameter = 20.0
thickness = 10.0
slot_width = 5.0
slot_length = 20.0
mount_hole_diameter = 5.0
mount_hole_radius = 30.0
mount_hole_count = 4

outer_radius = outer_diameter / 2.0
inner_radius = inner_diameter / 2.0

solid_body = Cylinder(outer_radius, thickness)
solid_body = solid_body - Cylinder(inner_radius, thickness)

slot_center_x = outer_radius - slot_length / 2.0
slot1 = Pos(slot_center_x, 0, 0) * Box(slot_length, slot_width, thickness)
slot2 = Pos(-slot_center_x, 0, 0) * Box(slot_length, slot_width, thickness)
solid_body = solid_body - slot1 - slot2

for i in range(mount_hole_count):
    angle = math.radians(i * 360.0 / mount_hole_count)
    px = mount_hole_radius * math.cos(angle)
    py = mount_hole_radius * math.sin(angle)
    solid_body = solid_body - Pos(px, py, 0) * Cylinder(mount_hole_diameter / 2, thickness)

part = solid_body
part.name = "flanged_disc_with_slots"
export_step(part, "output.step")