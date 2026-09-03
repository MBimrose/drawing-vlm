from build123d import *

plate_length = 80.0
plate_width = 60.0
plate_thickness = 2.0
rib_width = 10.0
rib_height = 1.5
vent_slot_length = 12.0
vent_slot_width = 3.0
vent_rows = 3
vent_cols = 4
vent_spacing_x = 15.0
vent_spacing_y = 12.0
mount_hole_dia = 4.0
mount_hole_offset = 6.0
chamfer_dist = 0.5

base = Box(plate_length, plate_width, plate_thickness)
base = chamfer(base.edges().filter_by(Axis.Z), chamfer_dist)

rib1 = Pos(0, 0, plate_thickness/2 + rib_height/2) * Box(rib_width, plate_length, rib_height)
rib2 = Pos(0, 0, plate_thickness/2 + rib_height/2) * Box(plate_width, rib_width, rib_height)

result = base + rib1 + rib2

for i in range(vent_cols):
    for j in range(vent_rows):
        x = (i - (vent_cols - 1) / 2) * vent_spacing_x
        y = (j - (vent_rows - 1) / 2) * vent_spacing_y
        slot = Pos(x, y, plate_thickness/2 + rib_height/2) * Box(vent_slot_length, vent_slot_width, plate_thickness + rib_height + 1)
        result = result - slot

hole_positions = [
    (-plate_length/2 + mount_hole_offset, -plate_width/2 + mount_hole_offset),
    ( plate_length/2 - mount_hole_offset, -plate_width/2 + mount_hole_offset),
    ( plate_length/2 - mount_hole_offset,  plate_width/2 - mount_hole_offset),
    (-plate_length/2 + mount_hole_offset,  plate_width/2 - mount_hole_offset),
]
for x, y in hole_positions:
    hole = Pos(x, y, 0) * Cylinder(mount_hole_dia/2, plate_thickness + 1)
    result = result - hole

part = result
part.name = "ventilated_plate_with_ribs"
export_step(part, "output.step")