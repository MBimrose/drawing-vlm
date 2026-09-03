from build123d import *

outer_length = 80.0
outer_width = 40.0
thickness = 12.0
wall_thickness = 4.0
tab_length = 20.0
tab_width = 8.0
hole_diameter = 5.0
hole_offset_x = 15.0
hole_offset_y = 10.0
chamfer_size = 1.0

base = Box(outer_length, outer_width, thickness)
tab = Pos(outer_length/2 + tab_length/2, 0, 0) * Box(tab_length, tab_width, thickness)
result = base + tab

inner_length = outer_length - 2 * wall_thickness
inner_width = outer_width - 2 * wall_thickness
cavity = Box(inner_length, inner_width, thickness)
result = result - cavity

hole_positions = [
    (-outer_length/2 + hole_offset_x, -outer_width/2 + hole_offset_y),
    ( outer_length/2 - hole_offset_x, -outer_width/2 + hole_offset_y),
    (-outer_length/2 + hole_offset_x,  outer_width/2 - hole_offset_y),
    ( outer_length/2 - hole_offset_x,  outer_width/2 - hole_offset_y),
]
for x, y in hole_positions:
    result = result - Pos(x, y, 0) * Cylinder(hole_diameter/2, thickness)

result = chamfer(result.edges().filter_by(Axis.Z), chamfer_size)

part = result
part.name = "plate_with_tab_and_holes"
export_step(part, "output.step")