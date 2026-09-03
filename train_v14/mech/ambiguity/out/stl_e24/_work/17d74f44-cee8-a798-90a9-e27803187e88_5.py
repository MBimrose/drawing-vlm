from build123d import *

outer_radius = 30.0
wall_thickness = 3.0
inner_radius = outer_radius - wall_thickness
sleeve_length = 80.0
groove_width = 4.0
groove_depth = 1.0
groove_length = sleeve_length * 0.6
boss_radius = 6.0
boss_height = 10.0
boss_offset = 8.0
boss_hole_diameter = 6.0
chamfer_size = 0.5

sleeve = Cylinder(outer_radius, sleeve_length) - Cylinder(inner_radius, sleeve_length)

groove_box = Pos(outer_radius - groove_width / 2, 0, 0) * Box(groove_width, groove_length, groove_depth)
sleeve = sleeve - groove_box

boss = Pos(outer_radius - boss_offset, -sleeve_length / 2 + boss_offset, 0) * Rot(0, 90, 0) * Cylinder(boss_radius, boss_height)
boss = chamfer(boss.edges(), chamfer_size)

boss_hole = Pos(outer_radius - boss_offset, -sleeve_length / 2 + boss_offset, 0) * Rot(0, 90, 0) * Cylinder(boss_hole_diameter / 2, boss_height + 2)
boss = boss - boss_hole

part = sleeve + boss
part.name = "sleeve_with_boss"
export_step(part, "output.step")