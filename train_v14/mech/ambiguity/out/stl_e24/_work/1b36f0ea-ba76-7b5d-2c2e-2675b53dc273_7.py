from build123d import *

plate_length = 80.0
plate_width = 60.0
plate_thickness = 5.0
rib_width = 8.0
rib_height = 2.0
rib_margin = 5.0
slot_width = 6.0
slot_length = 30.0
slot_spacing = 12.0
slot_count = 3
fillet_radius = 1.0
mount_hole_dia = 4.0
mount_hole_offset = 10.0

base = Pos(0, 0, plate_thickness / 2) * Box(plate_length, plate_width, plate_thickness)
rib_long = Pos(0, 0, plate_thickness + rib_height / 2) * Box(plate_length - 2 * rib_margin, rib_width, rib_height)
rib_cross = Pos(0, 0, plate_thickness + rib_height / 2) * Box(rib_width, plate_width - 2 * rib_margin, rib_height)

result = base + rib_long + rib_cross

slot_start_x = -((slot_count - 1) * (slot_width + slot_spacing)) / 2
for i in range(slot_count):
    x = slot_start_x + i * (slot_width + slot_spacing)
    slot = Pos(x, 0, (plate_thickness + rib_height) / 2) * Box(slot_width, slot_length, plate_thickness + rib_height)
    result = result - slot

hole_positions = [
    (-plate_length / 2 + mount_hole_offset, -plate_width / 2 + mount_hole_offset),
    ( plate_length / 2 - mount_hole_offset, -plate_width / 2 + mount_hole_offset),
    ( plate_length / 2 - mount_hole_offset,  plate_width / 2 - mount_hole_offset),
    (-plate_length / 2 + mount_hole_offset,  plate_width / 2 - mount_hole_offset),
]
for x, y in hole_positions:
    hole = Pos(x, y, (plate_thickness + rib_height) / 2) * Cylinder(mount_hole_dia / 2, plate_thickness + rib_height)
    result = result - hole

result = fillet(result.edges().filter_by(Axis.Z), fillet_radius)

part = result
part.name = "plate_with_ribs_slots_holes"
export_step(part, "output.step")