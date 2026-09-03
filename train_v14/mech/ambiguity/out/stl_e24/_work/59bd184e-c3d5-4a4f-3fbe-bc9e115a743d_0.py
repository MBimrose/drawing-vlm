from build123d import *

plate_length = 100.0
plate_width = 80.0
plate_thickness = 12.0
rib_width = 10.0
rib_height = 4.0
hole_diameter = 5.0
hole_spacing_x = 20.0
hole_spacing_y = 20.0
hole_rows = 3
hole_cols = 4
hole_margin = 10.0
chamfer_size = 1.0

base = Box(plate_length, plate_width, plate_thickness)
rib = Pos(0, 0, plate_thickness/2 - rib_height/2) * Box(rib_width, plate_width, rib_height)
solid_body = base + rib

slot = Pos(0, 0, plate_thickness/2 - rib_height/2) * Box(rib_width, plate_width, rib_height)
solid_body = solid_body - slot

for i in range(hole_cols):
    for j in range(hole_rows):
        x = -plate_length/2 + hole_margin + i * hole_spacing_x
        y = -plate_width/2 + hole_margin + j * hole_spacing_y
        solid_body = solid_body - Pos(x, y, 0) * Cylinder(hole_diameter/2, plate_thickness + 10)

solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_size)

part = solid_body
part.name = "plate_with_rib_and_holes"
export_step(part, "output.step")