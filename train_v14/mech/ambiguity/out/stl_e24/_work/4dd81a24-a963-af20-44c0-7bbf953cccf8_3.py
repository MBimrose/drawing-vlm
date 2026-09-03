from build123d import *

plate_length = 100.0
plate_width = 80.0
plate_thickness = 5.0
rib_height = 3.0
rib_width = 2.0
rib_margin = 5.0
hole_diameter = 4.5
hole_spacing_x = 30.0
hole_spacing_y = 30.0
hole_rows = 2
hole_cols = 2
hole_offset_x = 20.0
hole_offset_y = 20.0
chamfer_distance = 2.0

solid_body = Box(plate_length, plate_width, plate_thickness)
solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_distance)

rib = Pos(0, -plate_width/2 + rib_margin + rib_width/2, plate_thickness + rib_height/2) * Box(plate_length - 2*rib_margin, rib_width, rib_height)
solid_body = solid_body + rib

for i in range(hole_cols):
    for j in range(hole_rows):
        x = -plate_length/2 + hole_offset_x + i * hole_spacing_x
        y = -plate_width/2 + hole_offset_y + j * hole_spacing_y
        solid_body = solid_body - Pos(x, y, 0) * Cylinder(hole_diameter/2, plate_thickness + rib_height + 10)

part = solid_body
part.name = "plate_with_rib_and_holes"
export_step(part, "output.step")