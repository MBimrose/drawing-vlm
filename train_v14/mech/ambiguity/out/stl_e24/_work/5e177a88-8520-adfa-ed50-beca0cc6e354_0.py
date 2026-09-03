from build123d import *

block_length = 80.0
block_width = 80.0
block_height = 30.0
boss_diameter = 30.0
boss_height = 15.0
pocket_diameter = 40.0
pocket_depth = 12.0
chamfer_distance = 2.0
hole_diameter = 5.0
hole_offset_x = 30.0
hole_offset_y = 15.0

base = Pos(0, 0, block_height/2) * Box(block_length, block_width, block_height)
boss = Pos(0, 0, boss_height/2) * Cylinder(boss_diameter/2, boss_height)
result = base + boss

pocket = Pos(0, 0, block_height - pocket_depth/2) * Cylinder(pocket_diameter/2, pocket_depth)
result = result - pocket

bottom_face = result.faces().sort_by(Axis.Z)[0]
result = chamfer(bottom_face.edges(), chamfer_distance)

hole = Pos(hole_offset_x, 0, block_height/2) * Rot(90, 0, 0) * Cylinder(hole_diameter/2, block_width + 10)
result = result - hole

part = result
part.name = "block_with_boss_pocket_and_hole"
export_step(part, "output.step")