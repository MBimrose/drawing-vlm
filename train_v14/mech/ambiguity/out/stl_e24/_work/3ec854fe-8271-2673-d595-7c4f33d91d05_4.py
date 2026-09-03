from build123d import *

plate_length = 100.0
plate_width = 80.0
plate_thickness = 6.0
rib_height = 4.0
rib_width = 8.0
rib_offset = 10.0
hole_diameter = 5.0
hole_spacing_x = 30.0
hole_spacing_y = 20.0
hole_rows = 2
hole_cols = 3
chamfer_distance = 0.8

base = Box(plate_length, plate_width, plate_thickness)
rib1 = Box(plate_length - 2 * rib_offset, rib_width, rib_height)
rib2 = Box(rib_width, plate_width - 2 * rib_offset, rib_height)

solid_body = base + rib1 + rib2

for i in range(hole_cols):
    for j in range(hole_rows):
        x = (i - (hole_cols - 1) / 2) * hole_spacing_x
        y = (j - (hole_rows - 1) / 2) * hole_spacing_y
        solid_body = solid_body - Pos(x, y, plate_thickness / 2) * Cylinder(hole_diameter / 2, plate_thickness)

solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_distance)

part = solid_body
part.name = "plate_with_ribs_and_holes"
export_step(part, "output.step")