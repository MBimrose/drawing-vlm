from build123d import *

outer_diameter = 60
length = 80
wall_thickness = 3
inner_diameter = outer_diameter - 2 * wall_thickness
boss_diameter = 12
boss_height = 8
boss_center_z = length / 2
thread_hole_diameter = 6
chamfer_size = 1
slot_width = 4
slot_depth = 2

outer_cyl = Cylinder(outer_diameter / 2, length)
inner_cyl = Cylinder(inner_diameter / 2, length)
tube = outer_cyl - inner_cyl

boss = Pos(outer_diameter / 2 - boss_height / 2, -boss_center_z, 0) * Rot(0, 90, 0) * Cylinder(boss_diameter / 2, boss_height)
boss = chamfer(boss.edges(), chamfer_size)

result = tube + boss

hole = Pos(outer_diameter / 2 - boss_height / 2, -boss_center_z, 0) * Rot(0, 90, 0) * Cylinder(thread_hole_diameter / 2, boss_height + 2)
result = result - hole

slot = Pos(outer_diameter / 2 - wall_thickness / 2, 0, 0) * Box(slot_width, length, slot_depth)
result = result - slot

part = result
part.name = "tube_with_boss_and_slot"
export_step(part, "output.step")