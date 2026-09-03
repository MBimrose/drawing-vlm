from build123d import *

plate_width = 80.0
plate_depth = 60.0
plate_thickness = 8.0
chamfer_size = 2.0
mount_hole_dia = 5.0
mount_hole_offset = 10.0
vent_hole_dia = 4.0
vent_rows = 4
vent_cols = 6
vent_spacing_x = 12.0
vent_spacing_y = 12.0
vent_offset_x = 10.0
vent_offset_y = 10.0
rib_width = 6.0
rib_depth = 30.0
rib_height = 4.0

base = Pos(-plate_width/2, -plate_depth/2, plate_thickness/2) * Box(plate_width, plate_depth, plate_thickness)
base = chamfer(base.edges().filter_by(Axis.Z), chamfer_size)

mount_pts = [
    (mount_hole_offset, mount_hole_offset),
    (plate_width - mount_hole_offset, mount_hole_offset),
    (mount_hole_offset, plate_depth - mount_hole_offset),
    (plate_width - mount_hole_offset, plate_depth - mount_hole_offset),
]
for x, y in mount_pts:
    base = base - Pos(x, y, plate_thickness/2) * Cylinder(mount_hole_dia/2, plate_thickness + 1)

vent_pts = []
for i in range(vent_cols):
    for j in range(vent_rows):
        x = vent_offset_x + i * vent_spacing_x
        y = vent_offset_y + j * vent_spacing_y
        if x + vent_hole_dia/2 > plate_width - mount_hole_offset:
            continue
        if y + vent_hole_dia/2 > plate_depth - mount_hole_offset:
            continue
        vent_pts.append((x, y))
for x, y in vent_pts:
    base = base - Pos(x, y, plate_thickness/2) * Cylinder(vent_hole_dia/2, plate_thickness + 1)

rib = Pos(-plate_width/2, -plate_depth/2, rib_height/2) * Box(rib_width, rib_depth, rib_height)
part = base + rib
part.name = "plate_with_vents_and_rib"
export_step(part, "output.step")