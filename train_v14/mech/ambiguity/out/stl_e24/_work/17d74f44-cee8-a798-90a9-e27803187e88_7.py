from build123d import *

outer_radius = 30
wall_thickness = 3
inner_radius = outer_radius - wall_thickness
length = 80
boss_radius = 6
boss_height = 8
boss_center_z = length / 2
hole_diameter = 6
slot_width = 20
slot_depth = 2
slot_center_z = length * 0.25
chamfer_size = 0.5

tube = Cylinder(outer_radius, length) - Cylinder(inner_radius, length)

boss = Pos(inner_radius - boss_height / 2, -boss_center_z, 0) * Rot(90, 0, 0) * Cylinder(boss_radius, boss_height)

result = tube + boss

hole = Pos(outer_radius, -boss_center_z, 0) * Rot(0, 90, 0) * Cylinder(hole_diameter / 2, wall_thickness + boss_height + 2)
result = result - hole

slot = Pos(outer_radius - slot_depth / 2, 0, slot_center_z) * Box(slot_depth, slot_width, slot_depth)
slot = chamfer(slot.edges(), chamfer_size)
result = result - slot

part = result
part.name = "tube_with_boss_and_slot"
export_step(part, "output.step")