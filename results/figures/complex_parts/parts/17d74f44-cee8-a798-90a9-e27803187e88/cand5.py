from build123d import *

outer_radius = 30.0
wall_thickness = 3.0
inner_radius = outer_radius - wall_thickness
length = 80.0
boss_radius = 6.0
boss_height = 8.0
boss_offset = 30.0
hole_diameter = 6.0
chamfer_size = 0.5
groove_width = 2.0
groove_length = 20.0
groove_depth = 1.0

result = Cylinder(outer_radius, length) - Cylinder(inner_radius, length)

boss = Pos(boss_offset, -boss_height/2, 0) * Rot(90, 0, 0) * Cylinder(boss_radius, boss_height)
boss = chamfer(boss.edges(), chamfer_size)
result = result + boss

hole = Pos(boss_offset, -boss_height/2, 0) * Rot(0, 90, 0) * Cylinder(hole_diameter/2, boss_height + 2)
result = result - hole

groove = Pos(inner_radius - groove_depth/2, 0, 0) * Box(groove_width, groove_length, groove_depth)
result = result - groove

part = result
part.name = "hollow_cylinder_with_boss_and_groove"
export_step(part, "output.step")