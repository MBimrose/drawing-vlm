from build123d import *

block_length = 80.0
block_width = 40.0
block_height = 20.0
pocket_radius = 12.0
pocket_depth = 4.0
hole_diameter = 5.0
hole_spacing = 30.0
chamfer_size = 1.0
boss_radius = 10.0
boss_height = 10.0

with BuildPart() as p:
    with BuildSketch() as s:
        Rectangle(block_length, block_width)
    extrude(amount=block_height)

solid_body = p.part

# Pocket on >X face: circle radius 12, cutBlind -4
pocket = Pos(block_length/2 - pocket_depth/2, 0, block_height/2) * Rot(0, 90, 0) * Cylinder(pocket_radius, pocket_depth)
solid_body = solid_body - pocket

# Boss on >Z face: cylinder radius 10, height 10
boss = Pos(0, 0, block_height/2 + boss_height/2) * Cylinder(boss_radius, boss_height)
solid_body = solid_body + boss

# 4 holes on >Z face: 2x2 array, spacing 30, diameter 5
for i in range(2):
    for j in range(2):
        x = (i - 0.5) * hole_spacing
        y = (j - 0.5) * hole_spacing
        hole = Pos(x, y, block_height/2) * Cylinder(hole_diameter/2, block_height + 10)
        solid_body = solid_body - hole

# Chamfer all vertical edges
vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = chamfer(vertical_edges, chamfer_size)

part = solid_body
part.name = "block_with_pocket_boss_holes"
export_step(part, "output.step")