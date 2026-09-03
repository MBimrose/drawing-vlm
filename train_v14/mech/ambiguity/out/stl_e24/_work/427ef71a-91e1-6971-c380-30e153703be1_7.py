from build123d import *

outer_width = 60.0
outer_depth = 60.0
outer_height = 30.0
wall_thickness = 5.0
opening_width = 30.0
opening_height = 20.0
opening_chamfer = 1.0
hole_diameter = 5.0
hole_offset_y = 0.0

inner_width = outer_width - 2 * wall_thickness
inner_depth = outer_depth - 2 * wall_thickness

solid_body = Pos(0, 0, outer_height / 2) * Box(outer_width, outer_depth, outer_height)
top_face = solid_body.faces().sort_by(Axis.Z)[-1]
bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face, bottom_face])

opening = Pos(0, -outer_depth / 2 + wall_thickness / 2, 0) * Box(opening_width, wall_thickness, opening_height)
solid_body = solid_body - opening

bottom_front_edge = solid_body.edges().filter_by(Axis.X).sort_by(Axis.Y)[-1:].sort_by(Axis.Z)[:1]
solid_body = chamfer(bottom_front_edge, opening_chamfer)

hole = Pos(0, -outer_depth / 2 + wall_thickness / 2, 0) * Cylinder(hole_diameter / 2, wall_thickness)
solid_body = solid_body - hole

part = solid_body
part.name = "hollow_box_with_opening"
export_step(part, "output.step")