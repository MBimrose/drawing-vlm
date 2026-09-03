from build123d import *

plate_length = 80.0
plate_width = 60.0
plate_thickness = 8.0
rib_length = 30.0
rib_width = 8.0
rib_height = 4.0
hole_diameter = 4.0
hole_spacing_x = 12.0
hole_spacing_y = 12.0
hole_rows = 2
hole_cols = 3
hole_offset_x = 10.0
hole_offset_y = 10.0
mount_hole_diameter = 5.0
mount_hole_offset = 10.0
chamfer_distance = 2.0

base = Pos(0, 0, plate_thickness/2) * Box(plate_length, plate_width, plate_thickness)
rib = Pos(0, 0, rib_height/2) * Box(rib_length, rib_width, rib_height)
result = base + rib

hole_points = []
for i in range(hole_cols):
    for j in range(hole_rows):
        x = hole_offset_x + i * hole_spacing_x
        y = hole_offset_y + j * hole_spacing_y
        hole_points.append((x, y))

for x, y in hole_points:
    result = result - Pos(x, y, plate_thickness/2) * Cylinder(hole_diameter/2, plate_thickness + 10)

corner_offsets = [
    (mount_hole_offset, mount_hole_offset),
    (plate_length - mount_hole_offset, mount_hole_offset),
    (mount_hole_offset, plate_width - mount_hole_offset),
    (plate_length - mount_hole_offset, plate_width - mount_hole_offset),
]
for x, y in corner_offsets:
    result = result - Pos(x, y, plate_thickness/2) * Cylinder(mount_hole_diameter/2, plate_thickness + 10)

vertical_edges = result.edges().filter_by(Axis.Z)
result = chamfer(vertical_edges, chamfer_distance)

part = result
part.name = "plate_with_rib_and_holes"
export_step(part, "output.step")