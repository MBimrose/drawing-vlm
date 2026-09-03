from build123d import *

plate_length = 100.0
plate_width = 80.0
plate_thickness = 12.0
rib_width = 12.0
rib_height = 4.0
groove_width = 10.0
groove_depth = 4.0
hole_diameter = 5.0
hole_spacing_x = 20.0
hole_spacing_y = 20.0
hole_rows = 3
hole_cols = 4
chamfer_size = 1.0

solid_body = Box(plate_length, plate_width, plate_thickness)
solid_body = solid_body + Pos(0, 0, plate_thickness/2 - rib_height/2) * Box(rib_width, plate_width, rib_height)
solid_body = solid_body - Pos(0, 0, plate_thickness/2 - groove_depth/2) * Box(groove_width, plate_length, groove_depth)

for i in range(hole_cols):
    for j in range(hole_rows):
        x = (i - (hole_cols - 1) / 2) * hole_spacing_x
        y = (j - (hole_rows - 1) / 2) * hole_spacing_y
        solid_body = solid_body - Pos(x, y, 0) * Cylinder(hole_diameter/2, plate_thickness + 10)

solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_size)

part = solid_body
part.name = "plate_with_rib_groove_holes"
export_step(part, "output.step")