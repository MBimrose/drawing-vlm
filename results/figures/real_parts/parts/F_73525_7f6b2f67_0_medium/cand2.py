from build123d import *

outer_diameter = 80.0
length = 20.0
wall_thickness = 4.0
boss_width = 15.0
boss_height = 10.0
boss_depth = 8.0
fillet_radius = 1.0
mount_hole_dia = 5.0
slot_width = 6.0
slot_length = 12.0

outer_radius = outer_diameter / 2.0
inner_radius = outer_radius - wall_thickness

result = Rot(0, 90, 0) * Cylinder(outer_radius, length)
result = result - Rot(0, 90, 0) * Cylinder(inner_radius, length)

boss = Pos(length/2 + boss_depth/2, 0, 0) * Box(boss_depth, boss_width, boss_height)
boss = fillet(boss.edges(), fillet_radius)
result = result + boss

for angle in [0, 90, 180, 270]:
    hole = Rot(0, angle, 0) * Pos(outer_radius - wall_thickness/2, 0, 0) * Rot(0, 90, 0) * Cylinder(mount_hole_dia/2, wall_thickness + 2)
    result = result - hole

slot = Pos(outer_radius - wall_thickness/2, 0, 0) * Box(wall_thickness + 2, slot_width, slot_length)
result = result - slot

part = result
part.name = "hollow_cylinder_with_boss"
export_step(part, "output.step")