from build123d import *

plate_length = 80.0
plate_width = 60.0
plate_thickness = 5.0
pocket_length = 40.0
pocket_width = 30.0
pocket_depth = 3.0
vent_hole_diameter = 3.0
vent_rows = 4
vent_cols = 6
vent_spacing = 8.0
mount_hole_diameter = 5.0
mount_hole_offset = 8.0
rib_thickness = 2.0
rib_height = 2.0
rib_spacing = 20.0
chamfer_size = 1.0

result = Box(plate_length, plate_width, plate_thickness)
result = chamfer(result.edges().filter_by(Axis.Z), chamfer_size)

pocket = Pos(0, 0, plate_thickness/2 - pocket_depth/2) * Box(pocket_length, pocket_width, pocket_depth)
result = result - pocket

vent_start_x = -((vent_cols - 1) * vent_spacing) / 2
vent_start_y = -((vent_rows - 1) * vent_spacing) / 2
for i in range(vent_cols):
    for j in range(vent_rows):
        x = vent_start_x + i * vent_spacing
        y = vent_start_y + j * vent_spacing
        result = result - Pos(x, y, 0) * Cylinder(vent_hole_diameter/2, plate_thickness)

mount_points = [
    (-plate_length/2 + mount_hole_offset, -plate_width/2 + mount_hole_offset),
    (plate_length/2 - mount_hole_offset, -plate_width/2 + mount_hole_offset),
    (-plate_length/2 + mount_hole_offset, plate_width/2 - mount_hole_offset),
    (plate_length/2 - mount_hole_offset, plate_width/2 - mount_hole_offset),
]
for x, y in mount_points:
    result = result - Pos(x, y, 0) * Cylinder(mount_hole_diameter/2, plate_thickness)

rib_count = int((plate_length - 2 * mount_hole_offset) // rib_spacing)
for i in range(rib_count):
    x_pos = -plate_length/2 + mount_hole_offset + (i + 0.5) * rib_spacing
    rib = Pos(x_pos, 0, rib_height/2) * Box(rib_thickness, plate_width - 2 * mount_hole_offset, rib_height)
    result = result + rib

part = result
part.name = "plate_with_pocket_vents_mounts_ribs"
export_step(part, "output.step")