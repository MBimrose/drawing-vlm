from build123d import *

block_length = 60.0
block_width = 40.0
block_height = 20.0
boss_diameter = 20.0
boss_height = 10.0
hole_diameter = 6.0
hole_offset_x = 15.0
hole_offset_y = 10.0
fillet_radius = 2.0
pocket_length = 30.0
pocket_width = 20.0
pocket_depth = 8.0

with BuildPart() as p:
    with BuildSketch() as s:
        Rectangle(block_length, block_width)
    extrude(amount=block_height)
    with BuildSketch() as s2:
        Circle(boss_diameter / 2)
    extrude(amount=boss_height)

solid_body = p.part
solid_body = fillet(solid_body.edges(), fillet_radius)

hole_positions = [
    (hole_offset_x, hole_offset_y),
    (-hole_offset_x, hole_offset_y),
    (hole_offset_x, -hole_offset_y),
    (-hole_offset_x, -hole_offset_y),
]
for x, y in hole_positions:
    solid_body = solid_body - Pos(x, y, 0) * Cylinder(hole_diameter / 2, 100)

pocket = Pos(-block_length / 4, -block_width / 4, pocket_depth / 2) * Box(pocket_length, pocket_width, pocket_depth)
solid_body = solid_body - pocket

part = solid_body
part.name = "block_with_boss_holes_pocket"
export_step(part, "output.step")