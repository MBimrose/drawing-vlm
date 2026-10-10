from build123d import *

outer_radius = 30.0
wall_thickness = 3.0
inner_radius = outer_radius - wall_thickness
length = 80.0
rib_thickness = 2.0
rib_height = 20.0
rib_width = 10.0
slot_width = 6.0
slot_height = 12.0
boss_radius = 6.0
boss_height = 8.0
boss_hole_dia = 6.0
chamfer_size = 1.0

result = Cylinder(outer_radius, length) - Cylinder(inner_radius, length)

rib = Pos(inner_radius - rib_thickness/2, 0, 0) * Box(rib_width, rib_height, rib_thickness)
result = result + rib

slot = Pos(outer_radius - wall_thickness/2, 0, 0) * Box(wall_thickness, slot_width, slot_height)
result = result - slot

boss = Pos(outer_radius - boss_height/2, -boss_height/2, 0) * Rot(0, 90, 0) * Cylinder(boss_radius, boss_height)
boss = chamfer(boss.edges(), chamfer_size)
result = result + boss

hole = Pos(outer_radius - boss_height/2, -boss_height/2, 0) * Rot(0, 90, 0) * Cylinder(boss_hole_dia/2, boss_height + 2)
result = result - hole

part = result
part.name = "hollow_cylinder_with_rib_slot_boss"
export_step(part, "output.step")