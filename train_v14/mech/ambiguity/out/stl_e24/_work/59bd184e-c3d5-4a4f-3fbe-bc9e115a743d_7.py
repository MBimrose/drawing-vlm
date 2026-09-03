from build123d import *

base_length = 100.0
base_width = 80.0
base_thickness = 12.0
groove_width = 12.0
groove_depth = 4.0
hole_diameter = 5.0
hole_spacing_x = 20.0
hole_spacing_y = 20.0
hole_margin = 10.0
chamfer_size = 1.0

solid_body = Box(base_length, base_width, base_thickness)

groove = Pos(0, 0, base_thickness/2 - groove_depth/2) * Box(groove_width, base_width, groove_depth)
solid_body = solid_body - groove

cols = int((base_length - 2 * hole_margin) // hole_spacing_x)
rows = int((base_width - 2 * hole_margin) // hole_spacing_y)
start_x = -base_length / 2 + hole_margin
start_y = -base_width / 2 + hole_margin

for i in range(cols):
    for j in range(rows):
        x = start_x + i * hole_spacing_x
        y = start_y + j * hole_spacing_y
        solid_body = solid_body - Pos(x, y, 0) * Cylinder(hole_diameter/2, base_thickness)

solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_size)

part = solid_body
part.name = "base_plate_with_groove_and_holes"
export_step(part, "output.step")