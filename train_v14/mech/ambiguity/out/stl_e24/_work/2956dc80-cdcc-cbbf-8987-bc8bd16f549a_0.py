from build123d import *

outer_diameter = 80.0
thickness = 10.0
central_hole_diameter = 20.0
slot_width = 5.0
slot_length = 30.0
slot_offset = 2.0
mount_hole_diameter = 5.0
mount_hole_offset = 30.0

outer_radius = outer_diameter / 2.0
central_hole_radius = central_hole_diameter / 2.0
slot_center_distance = outer_radius - slot_length / 2.0

solid_body = Cylinder(outer_radius, thickness)
solid_body = solid_body - Cylinder(central_hole_radius, thickness)

slot1 = Pos(slot_center_distance, 0, 0) * Box(slot_length, slot_width, thickness)
slot2 = Pos(-slot_center_distance, 0, 0) * Box(slot_length, slot_width, thickness)
solid_body = solid_body - slot1 - slot2

hole1 = Pos(0, mount_hole_offset, 0) * Cylinder(mount_hole_diameter / 2.0, thickness)
hole2 = Pos(0, -mount_hole_offset, 0) * Cylinder(mount_hole_diameter / 2.0, thickness)
solid_body = solid_body - hole1 - hole2

part = solid_body
part.name = "flanged_disc_with_slots"
export_step(part, "output.step")