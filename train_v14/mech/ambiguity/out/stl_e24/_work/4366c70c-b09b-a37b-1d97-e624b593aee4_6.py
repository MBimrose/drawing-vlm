from build123d import *
import math

outer_diameter = 80.0
thickness = 10.0
bore_diameter = 20.0
slot_width = 6.0
slot_length = 20.0
slot_center_radius = outer_diameter/2 - slot_length/2 - 2.0
chamfer_distance = 1.0
mount_hole_diameter = 4.0
mount_hole_offset = slot_center_radius + slot_length/2 - 5.0

solid_body = Cylinder(outer_diameter/2, thickness) - Cylinder(bore_diameter/2, thickness)

for i in range(4):
    angle = math.radians(i * 90)
    px = slot_center_radius * math.cos(angle)
    py = slot_center_radius * math.sin(angle)
    solid_body = solid_body - Pos(px, py, 0) * Box(slot_width, slot_length, thickness)

for i in range(4):
    angle = math.radians(i * 90)
    px = mount_hole_offset * math.cos(angle)
    py = mount_hole_offset * math.sin(angle)
    solid_body = solid_body - Pos(px, py, 0) * Cylinder(mount_hole_diameter/2, thickness)

solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_distance)

part = solid_body
part.name = "flanged_disc_with_slots"
export_step(part, "output.step")