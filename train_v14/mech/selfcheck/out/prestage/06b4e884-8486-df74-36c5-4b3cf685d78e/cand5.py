from build123d import *

rail_length = 100.0
rail_width = 40.0
rail_thickness = 12.0
pocket_length = 60.0
pocket_width = 20.0
pocket_depth = 6.0
hole_diameter = 5.0
hole_spacing_x = 20.0
hole_spacing_y = 12.0
hole_rows = 2
hole_cols = 4
chamfer_distance = 1.0
rib_height = 3.0
rib_width = 10.0
rib_thickness = 3.0

solid_body = Box(rail_length, rail_width, rail_thickness)

pocket = Pos(0, 0, rail_thickness - pocket_depth/2) * Box(pocket_length, pocket_width, pocket_depth)
solid_body = solid_body - pocket

for i in range(hole_cols):
    for j in range(hole_rows):
        x = (i - (hole_cols - 1) / 2) * hole_spacing_x
        y = (j - (hole_rows - 1) / 2) * hole_spacing_y
        solid_body = solid_body - Pos(x, y, 0) * Cylinder(hole_diameter/2, rail_thickness + 10)

rib = Pos(0, 0, -rail_thickness/2 - rib_height/2) * Box(rib_width, rib_thickness, rib_height)
solid_body = solid_body + rib

front_face = solid_body.faces().sort_by(Axis.X)[-1]
solid_body = chamfer(front_face.edges(), chamfer_distance)

part = solid_body
part.name = "rail_with_pocket_holes_rib"
export_step(part, "output.step")