from build123d import *

plate_width = 80.0
plate_height = 60.0
plate_thickness = 5.0
rib_width = 4.0
rib_height = 2.0
rib_spacing = 10.0
hole_diameter = 3.0
hole_rows = 2
hole_cols = 4
hole_spacing_x = 10.0
hole_spacing_y = 12.0
mount_hole_diameter = 4.0
mount_hole_offset_y = 15.0
chamfer_size = 0.8

result = Box(plate_width, plate_height, plate_thickness)
result = chamfer(result.edges().filter_by(Axis.Z), chamfer_size)

rib_count = int((plate_width - rib_spacing) // rib_spacing)
for i in range(rib_count):
    x = (i - (rib_count - 1) / 2) * rib_spacing
    result = result + Pos(x, 0, -plate_thickness/2 + rib_height/2) * Box(rib_width, plate_height, rib_height)

for i in range(hole_cols):
    for j in range(hole_rows):
        x = (i - (hole_cols - 1) / 2) * hole_spacing_x
        y = (j - (hole_rows - 1) / 2) * hole_spacing_y
        result = result - Pos(x, y, 0) * Cylinder(hole_diameter/2, plate_thickness + 1)

for y in [mount_hole_offset_y, -mount_hole_offset_y]:
    result = result - Pos(0, y, 0) * Rot(0, 90, 0) * Cylinder(mount_hole_diameter/2, plate_width + 1)

part = result
part.name = "plate_with_ribs_and_holes"
export_step(part, "output.step")