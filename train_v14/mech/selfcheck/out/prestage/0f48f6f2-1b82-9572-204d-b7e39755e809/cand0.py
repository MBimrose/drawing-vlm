from build123d import *

outer_length = 80.0
outer_width = 50.0
outer_height = 30.0
wall_thickness = 3.0
rib_width = 30.0
rib_height = 10.0
chamfer_distance = 2.0
hole_diameter = 5.0

inner_length = outer_length - 2 * wall_thickness
inner_width = outer_width - 2 * wall_thickness
inner_height = outer_height - 2 * wall_thickness

base = Pos(0, 0, outer_height / 2) * Box(outer_length, outer_width, outer_height)
top_face = base.faces().sort_by(Axis.Z)[-1]
bottom_face = base.faces().sort_by(Axis.Z)[0]
base = offset(base, amount=-wall_thickness, openings=[top_face, bottom_face])

rib = Pos(0, 0, wall_thickness + rib_height / 2) * Box(inner_length, rib_width, rib_height)
base = base + rib

front_face = base.faces().sort_by(Axis.X)[-1]
front_edges = front_face.edges()
base = chamfer(front_edges, chamfer_distance)

hole = Pos(0, 0, outer_height / 2) * Cylinder(hole_diameter / 2, outer_height + 10)
base = base - hole

part = base
part.name = "shelled_box_with_rib"
export_step(part, "output.step")