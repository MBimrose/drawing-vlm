from build123d import *

outer_length = 100.0
outer_width = 60.0
outer_height = 30.0
wall_thickness = 2.0
rib_width = 10.0
rib_height = 5.0
rib_offset = 5.0
groove_width = 20.0
groove_depth = 3.0
groove_length = 80.0
hole_diameter = 5.0
hole_count = 5
chamfer_size = 0.8

solid_body = Box(outer_length, outer_width, outer_height)
solid_body = offset(solid_body, amount=-wall_thickness)

rib = Pos(0, outer_width/2 - rib_offset - rib_width/2, outer_height/2 + rib_height/2) * Box(rib_width, rib_height, rib_height)
solid_body = solid_body + rib

groove = Pos(0, 0, outer_height/2 - groove_depth/2) * Box(groove_length, groove_width, groove_depth)
solid_body = solid_body - groove

hole_spacing = outer_length / (hole_count + 1)
for i in range(hole_count):
    x = -outer_length/2 + hole_spacing * (i + 1)
    hole = Pos(x, 0, 0) * Cylinder(hole_diameter/2, outer_height + 10)
    solid_body = solid_body - hole

front_face = solid_body.faces().sort_by(Axis.X)[0]
solid_body = chamfer(front_face.edges(), chamfer_size)

part = solid_body
part.name = "shelled_box_with_rib_groove_holes"
export_step(part, "output.step")