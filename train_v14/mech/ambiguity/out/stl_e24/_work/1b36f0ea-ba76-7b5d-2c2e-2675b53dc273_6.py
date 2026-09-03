from build123d import *

plate_length = 80.0
plate_width = 60.0
plate_thickness = 5.0
rib_width = 8.0
rib_height = 2.0
slot_width = 6.0
slot_length = 30.0
slot_spacing = 12.0
fillet_radius = 1.0
mount_hole_dia = 4.0
mount_hole_offset = 10.0

base = Box(plate_length, plate_width, plate_thickness)
rib1 = Pos(0, 0, plate_thickness/2 + rib_height/2) * Box(plate_length - 2*mount_hole_offset, rib_width, rib_height)
rib2 = Pos(0, 0, plate_thickness/2 + rib_height/2) * Box(rib_width, plate_width - 2*mount_hole_offset, rib_height)
result = base + rib1 + rib2

slot_positions = [(-slot_spacing, 0), (0, 0), (slot_spacing, 0)]
for x, y in slot_positions:
    result = result - Pos(x, y, 0) * Box(slot_width, slot_length, plate_thickness)

hole_positions = [
    (plate_length/2 - mount_hole_offset, plate_width/2 - mount_hole_offset),
    (-plate_length/2 + mount_hole_offset, plate_width/2 - mount_hole_offset),
    (-plate_length/2 + mount_hole_offset, -plate_width/2 + mount_hole_offset),
    (plate_length/2 - mount_hole_offset, -plate_width/2 + mount_hole_offset)
]
for x, y in hole_positions:
    result = result - Pos(x, y, 0) * Cylinder(mount_hole_dia/2, plate_thickness)

result = fillet(result.edges().filter_by(Axis.Z), fillet_radius)

part = result
part.name = "plate_with_ribs_slots_holes"
export_step(part, "output.step")