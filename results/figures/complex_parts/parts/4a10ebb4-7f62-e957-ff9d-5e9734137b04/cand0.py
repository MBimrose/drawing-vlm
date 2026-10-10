from build123d import *

outer_length = 80.0
outer_width = 50.0
outer_height = 30.0
wall_thickness = 2.0
rib_height = 8.0
rib_thickness = 2.0
pocket_length = 40.0
pocket_width = 25.0
pocket_depth = 12.0
hole_diameter = 4.0
hole_offset_x = 20.0
hole_offset_y = 10.0

solid_body = Pos(0, 0, outer_height/2) * Box(outer_length, outer_width, outer_height)
bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[bottom_face])

rib = Pos(0, 0, -rib_height/2) * Box(outer_length, rib_thickness, rib_height)
solid_body = solid_body + rib

pocket = Pos(0, 0, outer_height - pocket_depth/2) * Box(pocket_length, pocket_width, pocket_depth)
solid_body = solid_body - pocket

for x, y in [(hole_offset_x, hole_offset_y), (-hole_offset_x, hole_offset_y),
             (hole_offset_x, -hole_offset_y), (-hole_offset_x, -hole_offset_y)]:
    solid_body = solid_body - Pos(x, y, outer_height/2) * Cylinder(hole_diameter/2, outer_height + 10)

part = solid_body
part.name = "shelled_box_with_rib_pocket_holes"
export_step(part, "output.step")