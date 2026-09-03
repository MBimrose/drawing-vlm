from build123d import *

outer_width = 80.0
outer_height = 60.0
frame_thickness = 5.0
extrude_depth = 20.0
inner_width = outer_width - 2 * frame_thickness
inner_height = outer_height - 2 * frame_thickness
chamfer_distance = 2.0
hole_diameter = 5.0

result = Box(outer_width, outer_height, extrude_depth)
result = result - Box(inner_width, inner_height, extrude_depth)
result = result - Cylinder(hole_diameter / 2, extrude_depth)
result = chamfer(result.edges().filter_by(Axis.Z), chamfer_distance)

part = result
part.name = "frame_with_hole"
export_step(part, "output.step")