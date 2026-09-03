from build123d import *

outer_length = 80.0
outer_width = 30.0
outer_height = 40.0
wall_thickness = 2.0
groove_width = 20.0
groove_depth = 6.0
groove_height = 10.0
hole_diameter = 4.0
hole_spacing = 20.0
chamfer_distance = 0.5

solid_body = Pos(0, 0, outer_height/2) * Box(outer_length, outer_width, outer_height)
top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face])

groove_box = Box(groove_width, groove_depth, groove_height)
solid_body = solid_body - Pos(0, outer_width/2 - groove_depth/2, outer_height - groove_height/2) * groove_box
solid_body = solid_body - Pos(0, -outer_width/2 + groove_depth/2, outer_height - groove_height/2) * groove_box

hole_cyl = Cylinder(hole_diameter/2, outer_height)
for x in [-hole_spacing/2, hole_spacing/2]:
    solid_body = solid_body - Pos(x, outer_width/2, outer_height/2) * hole_cyl
    solid_body = solid_body - Pos(x, -outer_width/2, outer_height/2) * hole_cyl

front_face = solid_body.faces().sort_by(Axis.X)[-1]
solid_body = chamfer(front_face.edges(), chamfer_distance)

part = solid_body
part.name = "hollow_box_with_grooves_and_holes"
export_step(part, "output.step")