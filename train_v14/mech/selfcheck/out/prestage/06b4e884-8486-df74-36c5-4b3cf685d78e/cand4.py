from build123d import *

rail_length = 100.0
rail_width = 40.0
rail_height = 12.0
wall_thickness = 4.0
rib_width = 10.0
rib_height = 3.0
rib_thickness = wall_thickness
hole_diameter = 5.0
hole_spacing_x = 20.0
hole_spacing_y = 12.0
hole_rows = 2
hole_cols = 4
chamfer_distance = 1.0

solid_body = Box(rail_length, rail_width, rail_height)
rib = Pos(0, 0, -rail_height/2 - rib_height/2) * Box(rib_width, rib_thickness, rib_height)
solid_body = solid_body + rib

for i in range(hole_cols):
    for j in range(hole_rows):
        x = (i - (hole_cols - 1) / 2) * hole_spacing_x
        y = (j - (hole_rows - 1) / 2) * hole_spacing_y
        solid_body = solid_body - Pos(x, y, 0) * Cylinder(hole_diameter/2, rail_height + rib_height + 10)

x_face = solid_body.faces().sort_by(Axis.X)[-1]
solid_body = chamfer(x_face.edges(), chamfer_distance)

part = solid_body
part.name = "rail_with_rib_and_holes"
export_step(part, "output.step")