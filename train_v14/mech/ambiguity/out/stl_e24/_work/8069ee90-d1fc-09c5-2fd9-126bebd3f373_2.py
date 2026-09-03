from build123d import *

plate_size = 80.0
plate_thickness = 5.0
edge_chamfer = 2.0
central_hole_diameter = 12.0
slot_length = 60.0
slot_width = 8.0
slot_offset = 5.0
mount_hole_diameter = 6.0
mount_hole_offset = 10.0
boss_diameter = 20.0
boss_height = 3.0
fillet_radius = 1.0

solid_body = Box(plate_size, plate_size, plate_thickness)
solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), edge_chamfer)

solid_body = solid_body - Cylinder(central_hole_diameter/2, plate_thickness + 1)

slot_center_offset = (plate_size / 2) - slot_offset - (slot_length / 2)
slot_positions = [
    (slot_center_offset, 0),
    (-slot_center_offset, 0),
    (0, slot_center_offset),
    (0, -slot_center_offset),
]
for x, y in slot_positions:
    solid_body = solid_body - Pos(x, y, 0) * Box(slot_length, slot_width, plate_thickness + 1)

mount_positions = [
    (plate_size/2 - mount_hole_offset, plate_size/2 - mount_hole_offset),
    (-plate_size/2 + mount_hole_offset, plate_size/2 - mount_hole_offset),
    (-plate_size/2 + mount_hole_offset, -plate_size/2 + mount_hole_offset),
    (plate_size/2 - mount_hole_offset, -plate_size/2 + mount_hole_offset),
]
for x, y in mount_positions:
    solid_body = solid_body - Pos(x, y, 0) * Cylinder(mount_hole_diameter/2, plate_thickness + 1)

solid_body = solid_body + Pos(0, 0, plate_thickness/2 - boss_height/2) * Cylinder(boss_diameter/2, boss_height)

solid_body = fillet(solid_body.edges().filter_by(Axis.Z), fillet_radius)

part = solid_body
part.name = "plate_with_slots_and_boss"
export_step(part, "output.step")