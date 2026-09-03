from build123d import *

plate_length = 80.0
plate_width = 60.0
plate_thickness = 5.0
rib_width = 4.0
rib_height = 2.0
rib_spacing = 8.0
hole_diameter = 3.0
hole_rows = 2
hole_cols = 4
hole_spacing_x = 10.0
hole_spacing_y = 12.0
mount_hole_diameter = 4.0
mount_hole_spacing = 30.0
chamfer_distance = 0.8

result = Box(plate_length, plate_width, plate_thickness)
result = chamfer(result.edges().filter_by(Axis.Z), chamfer_distance)

rib_count = int((plate_length - rib_spacing) // rib_spacing)
for i in range(rib_count):
    x_pos = -plate_length/2 + rib_spacing/2 + i * rib_spacing
    rib = Pos(x_pos, 0, -plate_thickness/2 + rib_height/2) * Box(rib_width, plate_width - 2*rib_spacing, rib_height)
    result = result + rib

for row in range(hole_rows):
    for col in range(hole_cols):
        x = (col - (hole_cols-1)/2) * hole_spacing_x
        y = (row - (hole_rows-1)/2) * hole_spacing_y
        result = result - Pos(x, y, 0) * Cylinder(hole_diameter/2, plate_thickness + 1)

for y in [-mount_hole_spacing/2, mount_hole_spacing/2]:
    result = result - Pos(0, y, 0) * Rot(0, 90, 0) * Cylinder(mount_hole_diameter/2, plate_length + 1)

part = result
part.name = "ribbed_plate_with_holes"
export_step(part, "output.step")