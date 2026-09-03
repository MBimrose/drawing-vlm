from build123d import *

outer_width = 60.0
outer_height = 40.0
length = 40.0
wall_thickness = 8.0
rib_thickness = 4.0
rib_height = 20.0
rib_offset = 5.0
clearance_hole_diameter = 12.0
chamfer_size = 1.0
relief_width = 6.0
relief_depth = 4.0
relief_offset = 10.0

inner_width = outer_width - 2 * wall_thickness
inner_height = outer_height - 2 * wall_thickness

result = Box(outer_width, outer_height, length)
result = result - Box(inner_width, inner_height, length)
result = chamfer(result.edges().filter_by(Axis.Z), chamfer_size)

rib = Pos(-outer_width/2 + wall_thickness + rib_thickness/2, 0, rib_offset + rib_height/2) * Box(rib_thickness, rib_thickness, rib_height)
result = result + rib

hole = Pos(0, 0, length/2 - wall_thickness/2) * Rot(0, 90, 0) * Cylinder(clearance_hole_diameter/2, outer_width)
result = result - hole

relief = Pos(-outer_width/2 + wall_thickness + relief_width/2, 0, length/2 - relief_offset - relief_depth/2) * Box(relief_width, relief_depth, relief_depth)
result = result - relief

part = result
part.name = "channel_with_rib_and_hole"
export_step(part, "output.step")