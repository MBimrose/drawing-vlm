from build123d import *

outer_diameter = 80.0
wall_thickness = 4.0
inner_diameter = outer_diameter - 2 * wall_thickness
length = 20.0
slot_width = 6.0
slot_depth = wall_thickness + 2.0
slot_length = length * 0.9
chamfer_size = 1.0
boss_diameter = 12.0
boss_height = 8.0

outer_radius = outer_diameter / 2.0
inner_radius = inner_diameter / 2.0

solid_body = Rot(0, 90, 0) * Cylinder(outer_radius, length)
solid_body = solid_body - Rot(0, 90, 0) * Cylinder(inner_radius, length)

slot_box = Pos(outer_radius - slot_depth / 2.0, 0, 0) * Box(slot_depth, slot_length, slot_width)
slot_box = chamfer(slot_box.edges(), chamfer_size)

for angle in [0, 90, 180, 270]:
    solid_body = solid_body - Rot(angle, 0, 0) * slot_box

boss = Pos(outer_radius + boss_height / 2.0, 0, 0) * Rot(0, 90, 0) * Cylinder(boss_diameter / 2.0, boss_height)
solid_body = solid_body + boss

part = solid_body
part.name = "hollow_cylinder_with_slots_and_boss"
export_step(part, "output.step")