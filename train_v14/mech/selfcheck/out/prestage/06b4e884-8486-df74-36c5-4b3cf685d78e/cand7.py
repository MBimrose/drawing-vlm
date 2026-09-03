from build123d import *

length = 100.0
width = 40.0
thickness = 12.0
rib_height = 3.0
rib_width = 10.0
rib_thickness = 3.0
hole_diameter = 5.0
hole_spacing_x = 20.0
hole_spacing_y = 12.0
hole_rows = 2
hole_cols = 4
chamfer_size = 1.0

solid_body = Box(length, width, thickness)
rib = Pos(0, 0, -thickness/2 - rib_height/2) * Box(rib_width, rib_thickness, rib_height)
solid_body = solid_body + rib

for i in range(hole_cols):
    for j in range(hole_rows):
        x = (i - (hole_cols - 1) / 2) * hole_spacing_x
        y = (j - (hole_rows - 1) / 2) * hole_spacing_y
        solid_body = solid_body - Pos(x, y, 0) * Cylinder(hole_diameter/2, thickness * 2)

x_face = solid_body.faces().sort_by(Axis.X)[-1]
solid_body = chamfer(x_face.edges(), chamfer_size)

part = solid_body
part.name = "plate_with_rib_and_holes"
export_step(part, "output.step")