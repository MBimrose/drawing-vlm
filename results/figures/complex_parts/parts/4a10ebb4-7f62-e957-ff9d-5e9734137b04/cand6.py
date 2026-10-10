from build123d import *

outer_length = 80.0
outer_width = 50.0
outer_height = 30.0
wall_thickness = 2.0
rib_height = 8.0
rib_thickness = 2.0
pocket_length = 40.0
pocket_width = 20.0
pocket_depth = 10.0
hole_diameter = 4.0
hole_spacing = 15.0

solid_body = Pos(0, 0, outer_height/2) * Box(outer_length, outer_width, outer_height)
bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[bottom_face])

rib = Pos(0, 0, -rib_height/2) * Box(outer_length - 2*wall_thickness, rib_thickness, rib_height)
solid_body = solid_body + rib

pocket = Pos(0, 0, outer_height - pocket_depth/2) * Box(pocket_length, pocket_width, pocket_depth)
solid_body = solid_body - pocket

for x, y in [(-hole_spacing, 0), (0, 0), (hole_spacing, 0)]:
    hole = Pos(x, y, outer_height/2) * Cylinder(hole_diameter/2, outer_height + 10)
    solid_body = solid_body - hole

part = solid_body
part.name = "hollow_box_with_rib_pocket_and_holes"
export_step(part, "output.step")