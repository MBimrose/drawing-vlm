from build123d import *

outer_length = 80.0
outer_width = 50.0
outer_height = 30.0
wall_thickness = 3.0
rib_thickness = 4.0
rib_height = 10.0
rib_offset_from_top = 10.0
chamfer_distance = 2.0
central_hole_diameter = 10.0

solid_body = Pos(0, 0, outer_height / 2) * Box(outer_length, outer_width, outer_height)

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face, bottom_face])

rib_center_z = outer_height - wall_thickness - rib_offset_from_top - rib_height / 2
rib = Pos(0, 0, rib_center_z) * Box(outer_length, rib_thickness, rib_height)
solid_body = solid_body + rib

hole = Pos(0, 0, outer_height / 2) * Cylinder(central_hole_diameter / 2, outer_height)
solid_body = solid_body - hole

front_face = solid_body.faces().sort_by(Axis.X)[-1]
front_edges = front_face.edges()
solid_body = chamfer(front_edges, chamfer_distance)

part = solid_body
part.name = "shelled_box_with_rib"
export_step(part, "output.step")