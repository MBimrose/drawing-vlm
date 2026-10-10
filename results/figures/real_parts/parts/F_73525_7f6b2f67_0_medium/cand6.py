from build123d import *

outer_diameter = 80.0
length = 20.0
wall_thickness = 4.0
slot_width = 6.0
slot_length = 30.0
boss_width = 12.0
boss_height = 8.0
chamfer_size = 1.0

outer_radius = outer_diameter / 2.0
inner_radius = outer_radius - wall_thickness

solid_body = Rot(0, 90, 0) * Cylinder(outer_radius, length)
solid_body = solid_body - Rot(0, 90, 0) * Cylinder(inner_radius, length)

slot_box = Box(length, slot_width, slot_length)
for angle in [0, 90, 180, 270]:
    solid_body = solid_body - Rot(angle, 0, 0) * slot_box

boss = Pos(length/2 + boss_height/2, 0, 0) * Box(boss_height, boss_width, boss_height)
boss = chamfer(boss.edges(), chamfer_size)
solid_body = solid_body + boss

part = solid_body
part.name = "hollow_cylinder_with_slots_and_boss"
export_step(part, "output.step")