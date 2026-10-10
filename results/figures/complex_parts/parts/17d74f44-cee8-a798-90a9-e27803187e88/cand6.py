from build123d import *

outer_radius = 30.0
wall_thickness = 3.0
inner_radius = outer_radius - wall_thickness
length = 80.0
boss_radius = 6.0
boss_height = 8.0
hole_diameter = 6.0
chamfer_size = 1.0
rib_thickness = 2.0
rib_width = 20.0
rib_height = 10.0

result = Cylinder(outer_radius, length) - Cylinder(inner_radius, length)

boss = Pos(inner_radius - boss_height/2, -boss_height/2, 0) * Rot(90, 0, 0) * Cylinder(boss_radius, boss_height)
result = result + boss

hole = Pos(inner_radius - (wall_thickness + 1)/2, -(wall_thickness + 1)/2, 0) * Rot(90, 0, 0) * Cylinder(hole_diameter/2, wall_thickness + 1)
result = result - hole

rib = Pos(inner_radius - rib_thickness/2, 0, 0) * Box(rib_thickness, rib_width, rib_height)
result = result + rib

y_edges = result.edges().filter_by(Axis.Y)
result = chamfer(y_edges, chamfer_size)

part = result
part.name = "hollow_cylinder_with_boss"
export_step(part, "output.step")