from build123d import *

block_length = 80.0
block_width = 80.0
block_height = 30.0
pocket_diameter = 40.0
pocket_depth = 12.0
boss_diameter = 20.0
boss_height = 10.0
chamfer_size = 2.0
hole_diameter = 5.0
hole_offset = 30.0

solid = Box(block_length, block_width, block_height)
solid = solid + Pos(0, 0, block_height/2 - boss_height/2) * Cylinder(boss_diameter/2, boss_height)
solid = solid - Pos(0, 0, block_height/2 - pocket_depth/2) * Cylinder(pocket_diameter/2, pocket_depth)
solid = solid - Pos(hole_offset, 0, 0) * Rot(90, 0, 0) * Cylinder(hole_diameter/2, block_width + 10)
bottom_face = solid.faces().sort_by(Axis.Z)[0]
solid = chamfer(bottom_face.edges(), chamfer_size)

part = solid
part.name = "block_with_boss_pocket_hole"
export_step(part, "output.step")