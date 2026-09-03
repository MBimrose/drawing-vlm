from build123d import *

plate_length = 100.0
plate_width = 80.0
plate_thickness = 12.0
groove_width = 10.0
groove_depth = 3.0
hole_diameter = 5.0
hole_spacing_x = 20.0
hole_spacing_y = 20.0
hole_margin = 10.0
chamfer_distance = 1.0
rib_width = 10.0
rib_height = 4.0
rib_spacing = 30.0

solid_body = Box(plate_length, plate_width, plate_thickness)

groove = Pos(0, 0, plate_thickness/2 - groove_depth/2) * Box(groove_width, plate_length, groove_depth)
solid_body = solid_body - groove

num_x = int((plate_length - 2 * hole_margin) // hole_spacing_x) + 1
num_y = int((plate_width - 2 * hole_margin) // hole_spacing_y) + 1
for i in range(num_x):
    for j in range(num_y):
        x = -plate_length/2 + hole_margin + i * hole_spacing_x
        y = -plate_width/2 + hole_margin + j * hole_spacing_y
        solid_body = solid_body - Pos(x, y, 0) * Cylinder(hole_diameter/2, plate_thickness)

rib1 = Pos(0, -rib_spacing/2, -plate_thickness/2 + rib_height/2) * Box(rib_width, plate_length, rib_height)
rib2 = Pos(0, rib_spacing/2, -plate_thickness/2 + rib_height/2) * Box(rib_width, plate_length, rib_height)
solid_body = solid_body + rib1 + rib2

solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_distance)

part = solid_body
part.name = "plate_with_groove_holes_ribs"
export_step(part, "output.step")