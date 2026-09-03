from build123d import *

outer_radius = 30.0
wall_thickness = 3.0
inner_radius = outer_radius - wall_thickness
length = 80.0
slot_width = 20.0
slot_depth = 2.0
boss_radius = 6.0
boss_height = 8.0
boss_offset = 25.0
chamfer_size = 1.0
hole_diameter = 6.0
hole_offset = 8.0

tube = Cylinder(outer_radius, length) - Cylinder(inner_radius, length)

slot_cut = Pos(outer_radius - slot_depth/2, 0, 0) * Box(slot_depth, slot_width, slot_depth)
tube = tube - slot_cut

boss = Pos(boss_offset, -outer_radius + boss_height/2, 0) * Rot(90, 0, 0) * Cylinder(boss_radius, boss_height)
boss = chamfer(boss.edges(), chamfer_size)

result = tube + boss

hole = Pos(outer_radius - wall_thickness/2, -hole_offset, 0) * Rot(0, 90, 0) * Cylinder(hole_diameter/2, wall_thickness + 2)
result = result - hole

part = result
part.name = "tube_with_boss_and_hole"
export_step(part, "output.step")