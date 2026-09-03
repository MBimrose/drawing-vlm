from build123d import *

cover_length = 80.0
cover_width = 60.0
cover_thickness = 5.0
wall_thickness = 2.0
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

result = Box(cover_length, cover_width, cover_thickness)
result = chamfer(result.edges().filter_by(Axis.Z), chamfer_size)

rib_count = int((cover_length - 2 * wall_thickness) // rib_spacing) + 1
for i in range(rib_count):
    x_pos = -cover_length / 2 + wall_thickness + i * rib_spacing
    rib = Pos(x_pos, 0, -cover_thickness / 2 + rib_height / 2) * Box(rib_width, cover_width - 2 * wall_thickness, rib_height)
    result = result + rib

for col in range(hole_cols):
    for row in range(hole_rows):
        x = (col - (hole_cols - 1) / 2) * hole_spacing_x
        y = (row - (hole_rows - 1) / 2) * hole_spacing_y
        result = result - Pos(x, y, 0) * Cylinder(hole_diameter / 2, cover_thickness * 2)

for y_off in [-cover_width / 2 + mount_hole_offset, cover_width / 2 - mount_hole_offset]:
    result = result - Pos(0, y_off, 0) * Rot(0, 90, 0) * Cylinder(mount_hole_diameter / 2, cover_length * 2)

part = result
part.name = "cover_plate_with_ribs"
export_step(part, "output.step")