from build123d import *

plate_length = 80.0
plate_width = 60.0
plate_thickness = 5.0
rib_height = 2.0
rib_width = 4.0
rib_spacing = 8.0
hole_diameter = 3.0
hole_spacing_x = 10.0
hole_spacing_y = 12.0
hole_rows = 2
hole_cols = 4
chamfer_size = 0.8
mount_hole_diameter = 4.0
mount_hole_offset = 15.0

result = Box(plate_length, plate_width, plate_thickness)
result = chamfer(result.edges().filter_by(Axis.Z), chamfer_size)

rib_count = int((plate_length - rib_spacing) // rib_spacing) + 1
for i in range(rib_count):
    x = (i - (rib_count - 1) / 2) * rib_spacing
    rib = Pos(x, 0, -plate_thickness/2 + rib_height/2) * Box(rib_width, plate_width - 2 * rib_spacing, rib_height)
    result = result + rib

for i in range(hole_cols):
    for j in range(hole_rows):
        x = (i - (hole_cols - 1) / 2) * hole_spacing_x
        y = (j - (hole_rows - 1) / 2) * hole_spacing_y
        result = result - Pos(x, y, 0) * Cylinder(hole_diameter/2, plate_thickness * 2)

for y in [-plate_width/4, plate_width/4]:
    result = result - Pos(0, y, 0) * Rot(0, 90, 0) * Cylinder(mount_hole_diameter/2, plate_length * 2)

part = result
part.name = "plate_with_ribs_and_holes"
export_step(part, "output.step")