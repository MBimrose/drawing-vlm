from build123d import *

outer_width = 80.0
outer_depth = 80.0
outer_height = 40.0
wall_thickness = 5.0
rib_thickness = 5.0
rib_height = 30.0
hole_diameter = 12.0
chamfer_distance = 2.0

base = Box(outer_width, outer_depth, outer_height)
top_face = base.faces().sort_by(Axis.Z)[-1]
base = offset(base, amount=-wall_thickness, openings=[top_face])

vertical_edges = base.edges().filter_by(Axis.Z)
base = chamfer(vertical_edges, chamfer_distance)

rib1 = Pos(0, 0, outer_height/2 - wall_thickness/2) * Box(outer_width - 2*wall_thickness, rib_thickness, rib_height)
rib2 = Pos(0, 0, outer_height/2 - wall_thickness/2) * Box(rib_thickness, outer_depth - 2*wall_thickness, rib_height)
base = base + rib1 + rib2

hole = Rot(0, 90, 0) * Cylinder(hole_diameter/2, outer_width + 10)
base = base - Pos(outer_width/2, 0, 0) * hole
base = base - Pos(-outer_width/2, 0, 0) * hole

part = base
part.name = "shelled_box_with_ribs_and_holes"
export_step(part, "output.step")