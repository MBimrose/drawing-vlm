from build123d import *

plate_width = 80.0
plate_depth = 60.0
plate_thickness = 5.0
fillet_radius = 2.0
rib_width = 5.0
rib_length = 50.0
rib_height = 5.0
rib_spacing = 15.0
rib_count = 4
hole_radius = 3.0
hole_pitch_x = 12.0
hole_pitch_y = 12.0
hole_rows = 4
hole_cols = 5

solid_body = Box(plate_width, plate_depth, plate_thickness)
solid_body = fillet(solid_body.edges(), fillet_radius)

rib_z = plate_thickness / 2 + rib_height / 2
for i in range(rib_count):
    x = (i - (rib_count - 1) / 2) * rib_spacing
    solid_body = solid_body + Pos(x, 0, rib_z) * Box(rib_width, rib_length, rib_height)

hole_h = plate_thickness + rib_height + 10
for i in range(hole_cols):
    for j in range(hole_rows):
        x = (i - (hole_cols - 1) / 2) * hole_pitch_x
        y = (j - (hole_rows - 1) / 2) * hole_pitch_y
        solid_body = solid_body - Pos(x, y, 0) * Cylinder(hole_radius, hole_h)

part = solid_body
part.name = "plate_with_ribs_and_holes"
export_step(part, "output.step")