from build123d import *

plate_width = 80.0
plate_height = 60.0
plate_thickness = 5.0
rib_width = 4.0
rib_height = 2.0
rib_spacing = 8.0
chamfer_size = 0.8
hole_diameter = 3.0
hole_spacing_x = 10.0
hole_spacing_y = 12.0
hole_rows = 2
hole_cols = 4
mount_hole_diameter = 4.0
mount_hole_offset = 15.0

result = Box(plate_width, plate_height, plate_thickness)
result = chamfer(result.edges().filter_by(Axis.Z), chamfer_size)

num_ribs = int((plate_width - rib_spacing) // rib_spacing) + 1
for i in range(num_ribs):
    x = -plate_width/2 + rib_spacing/2 + i * rib_spacing
    result = result + Pos(x, 0, -plate_thickness/2 + rib_height/2) * Box(rib_width, plate_height - 2*rib_spacing, rib_height)

for i in range(hole_cols):
    for j in range(hole_rows):
        x = -hole_spacing_x * (hole_cols - 1) / 2 + i * hole_spacing_x
        y = -hole_spacing_y * (hole_rows - 1) / 2 + j * hole_spacing_y
        result = result - Pos(x, y, 0) * Cylinder(hole_diameter/2, plate_thickness * 2)

result = result - Pos(0, -plate_height/2 + mount_hole_offset, 0) * Rot(0, 90, 0) * Cylinder(mount_hole_diameter/2, plate_width * 2)
result = result - Pos(0, plate_height/2 - mount_hole_offset, 0) * Rot(0, 90, 0) * Cylinder(mount_hole_diameter/2, plate_width * 2)

part = result
part.name = "plate_with_ribs_and_holes"
export_step(part, "output.step")