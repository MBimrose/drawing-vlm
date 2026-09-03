from build123d import *

outer_width = 80.0
outer_length = 80.0
outer_height = 40.0
wall_thickness = 5.0
rib_thickness = 5.0
rib_height = 5.0
chamfer_distance = 2.0
hole_diameter = 12.0

inner_width = outer_width - 2 * wall_thickness
inner_length = outer_length - 2 * wall_thickness
inner_height = outer_height - wall_thickness

base = Box(outer_width, outer_length, outer_height)
base = chamfer(base.edges().filter_by(Axis.Z), chamfer_distance)

cavity = Pos(0, 0, wall_thickness / 2) * Box(inner_width, inner_length, inner_height)
base = base - cavity

rib1 = Pos(0, 0, wall_thickness + rib_height / 2) * Box(inner_width - 2 * wall_thickness, rib_thickness, rib_height)
rib2 = Pos(0, 0, wall_thickness + rib_height / 2) * Box(rib_thickness, inner_length - 2 * wall_thickness, rib_height)
base = base + rib1 + rib2

hole = Rot(0, 90, 0) * Cylinder(hole_diameter / 2, outer_width + 10)
base = base - hole

part = base
part.name = "hollow_box_with_ribs_and_hole"
export_step(part, "output.step")