from build123d import *

plate_width = 80.0
plate_depth = 60.0
plate_thickness = 2.0
rib_width = 12.0
rib_height = 1.5
vent_slot_width = 3.0
vent_slot_length = 12.0
vent_spacing_x = 15.0
vent_spacing_y = 12.0
vent_rows = 3
vent_cols = 4
mount_hole_diameter = 4.0
mount_hole_offset = 6.0
chamfer_size = 0.5

base = Box(plate_width, plate_depth, plate_thickness)
base = chamfer(base.edges().filter_by(Axis.Z), chamfer_size)

rib = Pos(0, 0, plate_thickness/2 + rib_height/2) * Box(rib_width, plate_width, rib_height)
result = base + rib

vent_points = []
start_x = -plate_width/2 + vent_spacing_x
start_y = -plate_depth/2 + vent_spacing_y
for i in range(vent_cols):
    for j in range(vent_rows):
        x = start_x + i*vent_spacing_x
        y = start_y + j*vent_spacing_y
        vent_points.append((x, y))

for x, y in vent_points:
    slot = Pos(x, y, plate_thickness/2 + rib_height - plate_thickness/2) * Box(vent_slot_length, vent_slot_width, plate_thickness)
    result = result - slot

corner_x = plate_width/2 - mount_hole_offset
corner_y = plate_depth/2 - mount_hole_offset
mount_points = [
    (corner_x, corner_y),
    (-corner_x, corner_y),
    (-corner_x, -corner_y),
    (corner_x, -corner_y)
]

for x, y in mount_points:
    hole = Pos(x, y, 0) * Cylinder(mount_hole_diameter/2, plate_thickness + rib_height + 2)
    result = result - hole

part = result
part.name = "ventilated_plate_with_rib"
export_step(part, "output.step")