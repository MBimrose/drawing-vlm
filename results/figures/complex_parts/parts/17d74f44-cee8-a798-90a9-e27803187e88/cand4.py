from build123d import *

outer_radius = 30.0
wall_thickness = 3.0
inner_radius = outer_radius - wall_thickness
length = 80.0
rib_height = 12.0
rib_width = 20.0
rib_thickness = 2.0
rib_position = 40.0
hole_diameter = 6.0
hole_depth = 10.0
hole_offset = 8.0
chamfer_size = 0.5

result = Cylinder(outer_radius, length) - Cylinder(inner_radius, length)

rib = Pos(inner_radius - rib_thickness/2, -rib_width/2, 0) * Box(rib_thickness, rib_width, rib_height)
result = result + rib

hole = Pos(outer_radius - hole_depth/2, -hole_offset, 0) * Rot(0, 90, 0) * Cylinder(hole_diameter/2, hole_depth)
result = result - hole

result = chamfer(result.edges().filter_by(Axis.Z), chamfer_size)

part = result
part.name = "hollow_cylinder_with_rib_and_hole"
export_step(part, "output.step")