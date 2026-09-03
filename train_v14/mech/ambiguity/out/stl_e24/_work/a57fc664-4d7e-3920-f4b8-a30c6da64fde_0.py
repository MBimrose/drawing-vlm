from build123d import *

outer_width = 60.0
outer_depth = 40.0
outer_height = 40.0
wall_thickness = 8.0
groove_width = 6.0
groove_depth = 4.0
groove_offset_from_top = 10.0
groove_length = 30.0
side_hole_diameter = 12.0
side_hole_offset_from_top = 12.0
chamfer_size = 1.0

inner_width = outer_width - 2 * wall_thickness
inner_depth = outer_depth - 2 * wall_thickness

result = Box(outer_width, outer_depth, outer_height)
result = result - Box(inner_width, inner_depth, outer_height)

groove_z = outer_height / 2 - groove_offset_from_top - groove_depth / 2
groove = Pos(-outer_width / 2 + groove_length / 2, 0, groove_z) * Box(groove_length, groove_width, groove_depth)
result = result - groove

hole_z = outer_height / 2 - side_hole_offset_from_top
hole = Pos(0, 0, hole_z) * Rot(0, 90, 0) * Cylinder(side_hole_diameter / 2, outer_width)
result = result - hole

result = chamfer(result.edges().filter_by(Axis.Z), chamfer_size)

part = result
part.name = "hollow_box_with_groove_and_hole"
export_step(part, "output.step")