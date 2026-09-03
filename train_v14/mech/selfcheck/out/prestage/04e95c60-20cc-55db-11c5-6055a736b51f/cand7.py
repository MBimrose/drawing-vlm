from build123d import *
import math

outer_width = 80.0
outer_depth = 80.0
outer_height = 40.0
wall_thickness = 5.0
pocket_margin = 10.0
pocket_depth = 15.0
slot_width = 6.0
slot_length = 30.0
slot_depth = outer_height
slot_chamfer = 0.8
hole_diameter = 3.0
hole_depth = 8.0
hole_offset = 32.0

inner_width = outer_width - 2 * wall_thickness
inner_depth = outer_depth - 2 * wall_thickness
pocket_width = outer_width - 2 * pocket_margin
pocket_depth_dim = outer_depth - 2 * pocket_margin

result = Box(outer_width, outer_depth, outer_height)
result = result - Box(inner_width, inner_depth, outer_height - 2 * wall_thickness)
result = result - Pos(0, 0, outer_height - pocket_depth / 2) * Box(pocket_width, pocket_depth_dim, pocket_depth)

slot_box = Box(slot_depth, slot_width, slot_length)
result = result - Pos(-outer_width / 2 + slot_depth / 2, 0, 0) * slot_box

slot_edges = result.edges().filter_by(Axis.Z).sort_by(Axis.X)[:4]
result = chamfer(slot_edges, slot_chamfer)

for x, y in [(hole_offset, 0), (-hole_offset, 0), (0, hole_offset), (0, -hole_offset)]:
    result = result - Pos(x, y, outer_height - hole_depth / 2) * Cylinder(hole_diameter / 2, hole_depth)

part = result
part.name = "hollow_box_with_pocket_slot_holes"
export_step(part, "output.step")