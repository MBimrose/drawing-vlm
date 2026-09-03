from build123d import *

rail_length = 100.0
rail_width = 40.0
rail_thickness = 12.0
hole_diameter = 5.0
hole_spacing_x = 20.0
hole_spacing_y = 12.0
num_holes_x = 4
num_holes_y = 2
chamfer_size = 1.0
rib_height = 3.0
rib_width = 10.0
rib_thickness = 3.0

solid_body = Box(rail_length, rail_width, rail_thickness)

rib = Pos(0, 0, -rail_thickness/2 - rib_height/2) * Box(rib_width, rib_thickness, rib_height)
solid_body = solid_body + rib

for i in range(num_holes_x):
    for j in range(num_holes_y):
        x = (i - (num_holes_x - 1) / 2) * hole_spacing_x
        y = (j - (num_holes_y - 1) / 2) * hole_spacing_y
        solid_body = solid_body - Pos(x, y, 0) * Cylinder(hole_diameter/2, rail_thickness + rib_height + 10)

right_face = solid_body.faces().sort_by(Axis.X)[-1]
right_edges = right_face.edges()
solid_body = chamfer(right_edges, chamfer_size)

part = solid_body
part.name = "rail_with_rib_and_holes"
export_step(part, "output.step")