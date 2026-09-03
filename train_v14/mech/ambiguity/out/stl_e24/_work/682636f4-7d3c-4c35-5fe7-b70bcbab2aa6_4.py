from build123d import *

plate_width = 80.0
plate_height = 60.0
plate_thickness = 5.0
pocket_width = 40.0
pocket_height = 30.0
pocket_depth = 3.0
vent_hole_dia = 3.0
vent_spacing = 8.0
vent_rows = 4
vent_cols = 6
mount_hole_dia = 5.0
mount_hole_offset = 8.0
rib_thickness = 2.0
rib_height = 2.0
chamfer_size = 1.0

result = Box(plate_width, plate_height, plate_thickness)
result = chamfer(result.edges().filter_by(Axis.Z), chamfer_size)

pocket = Pos(0, 0, plate_thickness/2 - pocket_depth/2) * Box(pocket_width, pocket_height, pocket_depth)
result = result - pocket

rib1 = Pos(-pocket_width/4, 0, plate_thickness/2 - pocket_depth + rib_height/2) * Box(rib_thickness, pocket_height, rib_height)
rib2 = Pos(pocket_width/4, 0, plate_thickness/2 - pocket_depth + rib_height/2) * Box(rib_thickness, pocket_height, rib_height)
result = result + rib1 + rib2

for i in range(vent_cols):
    for j in range(vent_rows):
        x = (i - (vent_cols-1)/2) * vent_spacing
        y = (j - (vent_rows-1)/2) * vent_spacing
        result = result - Pos(x, y, 0) * Cylinder(vent_hole_dia/2, plate_thickness + 10)

corner_coords = [
    (plate_width/2 - mount_hole_offset, plate_height/2 - mount_hole_offset),
    (-plate_width/2 + mount_hole_offset, plate_height/2 - mount_hole_offset),
    (-plate_width/2 + mount_hole_offset, -plate_height/2 + mount_hole_offset),
    (plate_width/2 - mount_hole_offset, -plate_height/2 + mount_hole_offset),
]
for x, y in corner_coords:
    result = result - Pos(x, y, 0) * Cylinder(mount_hole_dia/2, plate_thickness + 10)

part = result
part.name = "plate_with_pocket_ribs_vents"
export_step(part, "output.step")