from build123d import *

outer_width = 50.0
outer_length = 60.0
outer_height = 30.0
wall_thickness = 5.0
rib_thickness = 2.0
rib_height = 15.0
chamfer_distance = 1.0
hole_diameter = 5.0
notch_width = 10.0
notch_depth = 5.0

inner_width = outer_width - 2 * wall_thickness
inner_length = outer_length - 2 * wall_thickness

base = Pos(0, 0, outer_height/2) * Box(outer_width, outer_length, outer_height)
top_face = base.faces().sort_by(Axis.Z)[-1]
bottom_face = base.faces().sort_by(Axis.Z)[0]
base = offset(base, amount=-wall_thickness, openings=[top_face, bottom_face])

rib = Pos(0, -outer_length/2 + wall_thickness + rib_thickness/2, rib_height/2) * Box(rib_thickness, inner_width, rib_height)
base = base + rib

hole = Pos(0, 0, outer_height/2) * Cylinder(hole_diameter/2, outer_height + 10)
base = base - hole

notch = Pos(0, outer_length/2 - notch_depth/2, outer_height/2) * Box(notch_width, notch_depth, outer_height + 10)
base = base - notch

front_face = base.faces().sort_by(Axis.Y)[-1]
front_bottom_edges = front_face.edges().sort_by(Axis.Z)[:1]
base = chamfer(front_bottom_edges, chamfer_distance)

part = base
part.name = "hollow_box_with_rib"
export_step(part, "output.step")