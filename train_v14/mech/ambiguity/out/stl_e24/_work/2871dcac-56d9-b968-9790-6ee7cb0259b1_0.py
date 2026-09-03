from build123d import *

outer_width = 80.0
outer_height = 60.0
thickness = 20.0
wall_thickness = 5.0
fillet_radius = 3.0
hole_diameter = 5.0

inner_width = outer_width - 2 * wall_thickness
inner_height = outer_height - 2 * wall_thickness

result = Box(outer_width, outer_height, thickness) - Box(inner_width, inner_height, thickness)
result = result - Cylinder(hole_diameter / 2, thickness)
result = fillet(result.edges().filter_by(Axis.Z), fillet_radius)

part = result
part.name = "hollow_frame_with_hole"
export_step(part, "output.step")