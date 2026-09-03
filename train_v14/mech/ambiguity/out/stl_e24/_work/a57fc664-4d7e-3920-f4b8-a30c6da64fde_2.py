from build123d import *

outer_width = 60.0
outer_depth = 40.0
outer_height = 40.0
wall_thickness = 8.0
base_thickness = 4.0
pocket_width = 30.0
pocket_depth = 20.0
pocket_height = 12.0
counterbore_diameter = 12.0
counterbore_depth = 6.0
through_hole_diameter = 6.0
chamfer_size = 1.0

inner_width = outer_width - 2 * wall_thickness
inner_depth = outer_depth - 2 * wall_thickness

base = Pos(0, 0, outer_height / 2) * Box(outer_width, outer_depth, outer_height)
inner_cut = Pos(0, 0, base_thickness + (outer_height - base_thickness) / 2) * Box(inner_width, inner_depth, outer_height - base_thickness)
result = base - inner_cut

pocket = Pos(0, 0, outer_height - pocket_height / 2) * Box(pocket_width, pocket_depth, pocket_height)
result = result - pocket

cbore = Pos(-outer_width / 2 + counterbore_depth / 2, 0, outer_height / 2 + wall_thickness) * Rot(0, 90, 0) * Cylinder(counterbore_diameter / 2, counterbore_depth)
result = result - cbore

thru = Pos(0, 0, outer_height / 2 + wall_thickness) * Rot(0, 90, 0) * Cylinder(through_hole_diameter / 2, outer_width + 10)
result = result - thru

vertical_edges = result.edges().filter_by(Axis.Z)
result = chamfer(vertical_edges, chamfer_size)

part = result
part.name = "box_with_pocket_and_holes"
export_step(part, "output.step")