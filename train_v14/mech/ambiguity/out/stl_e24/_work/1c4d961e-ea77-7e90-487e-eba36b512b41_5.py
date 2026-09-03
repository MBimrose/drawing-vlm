from build123d import *

outer_width = 80.0
outer_depth = 80.0
outer_height = 40.0
wall_thickness = 5.0
rib_height = 5.0
rib_thickness = 4.0
chamfer_size = 2.0
hole_diameter = 12.0

inner_width = outer_width - 2 * wall_thickness
inner_depth = outer_depth - 2 * wall_thickness

base = Box(outer_width, outer_depth, outer_height)
top_face = base.faces().sort_by(Axis.Z)[-1]
bottom_face = base.faces().sort_by(Axis.Z)[0]
base = offset(base, amount=-wall_thickness, openings=[top_face, bottom_face])

vertical_edges = base.edges().filter_by(Axis.Z)
base = chamfer(vertical_edges, chamfer_size)

rib_z = outer_height / 2 - rib_height / 2
rib1 = Pos(0, 0, rib_z) * Box(inner_width, rib_thickness, rib_height)
rib2 = Pos(0, 0, rib_z) * Box(rib_thickness, inner_depth, rib_height)
base = base + rib1 + rib2

hole_r = hole_diameter / 2
hole_h = outer_width + 10
hole_cyl = Rot(0, 90, 0) * Cylinder(hole_r, hole_h)
base = base - Pos(outer_width / 2, 0, 0) * hole_cyl
base = base - Pos(-outer_width / 2, 0, 0) * hole_cyl

part = base
part.name = "hollow_box_with_ribs_and_holes"
export_step(part, "output.step")