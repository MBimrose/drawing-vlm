from build123d import *

plate_length = 80.0
plate_width = 60.0
plate_thickness = 5.0
rib_width = 8.0
rib_height = 2.0
rib_margin = 10.0
slot_length = 30.0
slot_width = 6.0
slot_spacing_x = 18.0
slot_spacing_y = 20.0
num_slots_x = 3
num_slots_y = 2
fillet_radius = 1.0
mount_hole_dia = 4.0
mount_hole_offset = 10.0

base = Pos(0, 0, plate_thickness/2) * Box(plate_length, plate_width, plate_thickness)
rib1 = Pos(0, 0, plate_thickness + rib_height/2) * Box(plate_length - 2*rib_margin, rib_width, rib_height)
rib2 = Pos(0, 0, plate_thickness + rib_height/2) * Box(rib_width, plate_width - 2*rib_margin, rib_height)

solid_body = base + rib1 + rib2

slot_points = []
for i in range(num_slots_x):
    for j in range(num_slots_y):
        x = (i - (num_slots_x - 1) / 2) * slot_spacing_x
        y = (j - (num_slots_y - 1) / 2) * slot_spacing_y
        slot_points.append((x, y))

for x, y in slot_points:
    solid_body = solid_body - Pos(x, y, plate_thickness/2) * Box(slot_width, slot_length, plate_thickness)

hole_positions = [
    (plate_length/2 - mount_hole_offset, plate_width/2 - mount_hole_offset),
    (-plate_length/2 + mount_hole_offset, plate_width/2 - mount_hole_offset),
    (-plate_length/2 + mount_hole_offset, -plate_width/2 + mount_hole_offset),
    (plate_length/2 - mount_hole_offset, -plate_width/2 + mount_hole_offset),
]

for x, y in hole_positions:
    solid_body = solid_body - Pos(x, y, plate_thickness/2) * Cylinder(mount_hole_dia/2, plate_thickness)

solid_body = fillet(solid_body.edges().filter_by(Axis.Z), fillet_radius)

part = solid_body
part.name = "ribbed_plate_with_slots"
export_step(part, "output.step")