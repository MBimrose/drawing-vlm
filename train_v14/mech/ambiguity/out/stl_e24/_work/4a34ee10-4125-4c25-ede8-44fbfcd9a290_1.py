from build123d import *
import math

outer_radius = 45.0
inner_radius = 30.0
ring_thickness = 12.0
groove_width = 4.0
groove_depth = 6.0
slot_width = 4.0
slot_depth = 5.0
mount_hole_dia = 4.0
mount_hole_count = 4
mount_hole_offset_angle = 45.0

solid_body = Cylinder(outer_radius, ring_thickness)
solid_body = solid_body - Cylinder(inner_radius, ring_thickness)

groove_cyl = Pos(0, 0, ring_thickness/2 - groove_depth/2) * Cylinder(inner_radius - groove_width/2, groove_depth)
solid_body = solid_body - groove_cyl

slot_center_r = outer_radius - slot_depth/2
for i in range(4):
    angle = math.radians(i * 90)
    px = slot_center_r * math.cos(angle)
    py = slot_center_r * math.sin(angle)
    slot = Pos(px, py, 0) * Box(slot_depth, slot_width, ring_thickness)
    solid_body = solid_body - slot

hole_center_r = (inner_radius + outer_radius) / 2
for i in range(mount_hole_count):
    angle = math.radians(mount_hole_offset_angle + i * 360 / mount_hole_count)
    px = hole_center_r * math.cos(angle)
    py = hole_center_r * math.sin(angle)
    hole = Pos(px, py, 0) * Cylinder(mount_hole_dia/2, ring_thickness)
    solid_body = solid_body - hole

part = solid_body
part.name = "ring_with_groove_slots_and_mount_holes"
export_step(part, "output.step")