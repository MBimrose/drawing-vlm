from build123d import *

block_length = 80.0
block_width = 60.0
block_thickness = 12.0
wall_thickness = 2.0
boss_diameter = 20.0
boss_height = 8.0
fillet_radius = 1.5
chamfer_distance = 1.0
hole_diameter = 4.0
hole_offset = 10.0

solid_body = Box(block_length, block_width, block_thickness)

bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
solid_body = chamfer(bottom_face.edges(), chamfer_distance)

pocket = Pos(0, 0, wall_thickness / 2) * Box(block_length - 2 * wall_thickness, block_width - 2 * wall_thickness, block_thickness - wall_thickness)
solid_body = solid_body - pocket

boss = Pos(0, 0, block_thickness / 2 + boss_height / 2) * Cylinder(boss_diameter / 2, boss_height)
solid_body = solid_body + boss

solid_body = fillet(solid_body.edges().filter_by(Axis.Z), fillet_radius)

hole_positions = [
    (-block_length / 2 + hole_offset, -block_width / 2 + hole_offset),
    (block_length / 2 - hole_offset, -block_width / 2 + hole_offset),
    (-block_length / 2 + hole_offset, block_width / 2 - hole_offset),
    (block_length / 2 - hole_offset, block_width / 2 - hole_offset),
]
for x, y in hole_positions:
    solid_body = solid_body - Pos(x, y, 0) * Cylinder(hole_diameter / 2, block_thickness + boss_height + 10)

part = solid_body
part.name = "chamfered_block_with_boss"
export_step(part, "output.step")