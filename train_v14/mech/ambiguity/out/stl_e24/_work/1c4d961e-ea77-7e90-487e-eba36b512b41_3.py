from build123d import *

outer_size = 80.0
wall_thickness = 5.0
height = 40.0
rib_thickness = 3.0
rib_height = 5.0
hole_diameter = 12.0
chamfer_size = 2.0

inner_size = outer_size - 2 * wall_thickness

solid_body = Box(outer_size, outer_size, height)
top_face = solid_body.faces().sort_by(Axis.Z)[-1]
bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face, bottom_face])

vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = chamfer(vertical_edges, chamfer_size)

rib1 = Pos(0, 0, height/2 - rib_height/2) * Box(inner_size, rib_thickness, rib_height)
rib2 = Pos(0, 0, height/2 - rib_height/2) * Box(rib_thickness, inner_size, rib_height)
solid_body = solid_body + rib1 + rib2

hole = Pos(outer_size/2, 0, 0) * Rot(0, 90, 0) * Cylinder(hole_diameter/2, outer_size * 2)
solid_body = solid_body - hole

part = solid_body
part.name = "hollow_box_with_ribs_and_hole"
export_step(part, "output.step")