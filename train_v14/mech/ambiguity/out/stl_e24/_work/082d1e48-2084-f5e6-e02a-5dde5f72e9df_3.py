from build123d import *

block_length = 80.0
block_width = 50.0
block_height = 30.0
wall_thickness = 5.0
pocket_length = 50.0
pocket_width = 30.0
pocket_depth = block_height - wall_thickness
fillet_radius = 2.0
hole_diameter = 8.0
hole_depth = block_height - 2 * wall_thickness
boss_diameter = 15.0
boss_height = 10.0
boss_offset_x = 20.0

base = Pos(0, 0, block_height / 2) * Box(block_length, block_width, block_height)
boss = Pos(boss_offset_x, 0, block_height / 2) * Cylinder(boss_diameter / 2, boss_height)
solid_body = base + boss

pocket = Pos(0, 0, block_height - pocket_depth / 2) * Box(pocket_length, pocket_width, pocket_depth)
solid_body = solid_body - pocket

hole = Pos(block_length / 2 - hole_depth / 2, 0, block_height / 2) * Rot(0, 90, 0) * Cylinder(hole_diameter / 2, hole_depth)
solid_body = solid_body - hole

vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = fillet(vertical_edges, fillet_radius)

part = solid_body
part.name = "block_with_pocket_and_hole"
export_step(part, "output.step")