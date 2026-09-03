from build123d import *

plate_length = 100.0
plate_width = 80.0
plate_thickness = 12.0
groove_width = 10.0
groove_depth = 4.0
hole_diameter = 5.0
hole_spacing_x = 20.0
hole_spacing_y = 20.0
hole_margin = 10.0
chamfer_size = 1.0

solid_body = Box(plate_length, plate_width, plate_thickness)

groove = Pos(0, 0, plate_thickness/2 - groove_depth/2) * Box(groove_width, plate_width, groove_depth)
solid_body = solid_body - groove

num_x = int((plate_length - 2 * hole_margin) // hole_spacing_x)
num_y = int((plate_width - 2 * hole_margin) // hole_spacing_y)

for i in range(num_x):
    for j in range(num_y):
        x = -plate_length/2 + hole_margin + i * hole_spacing_x
        y = -plate_width/2 + hole_margin + j * hole_spacing_y
        hole = Pos(x, y, 0) * Cylinder(hole_diameter/2, plate_thickness)
        solid_body = solid_body - hole

vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = chamfer(vertical_edges, chamfer_size)

part = solid_body
part.name = "plate_with_groove_and_holes"
export_step(part, "output.step")