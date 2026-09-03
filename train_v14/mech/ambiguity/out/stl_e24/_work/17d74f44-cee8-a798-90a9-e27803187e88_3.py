from build123d import *

outer_radius = 30.0
wall_thickness = 3.0
length = 80.0
pocket_width = 12.0
pocket_height = 8.0
pocket_offset = 20.0
boss_radius = 6.0
boss_height = 8.0
boss_hole_diameter = 6.0
chamfer_size = 1.0
slot_width = 20.0
slot_depth = 2.0

inner_radius = outer_radius - wall_thickness

tube = Cylinder(outer_radius, length) - Cylinder(inner_radius, length)

pocket = Pos(outer_radius - pocket_height/2, -length/2 + pocket_offset, 0) * Box(pocket_height, pocket_width, pocket_height)
tube = tube - pocket

boss = Pos(outer_radius - boss_height/2, -length/2 + pocket_offset, 0) * Rot(0, 90, 0) * Cylinder(boss_radius, boss_height)
boss = chamfer(boss.edges(), chamfer_size)
tube = tube + boss

hole = Pos(outer_radius - boss_height/2, -length/2 + pocket_offset, 0) * Rot(0, 90, 0) * Cylinder(boss_hole_diameter/2, boss_height + 2)
tube = tube - hole

slot = Pos(inner_radius, 0, 0) * Box(length, slot_width, slot_depth)
tube = tube - slot

part = tube
part.name = "tube_with_pocket_boss_and_slot"
export_step(part, "output.step")