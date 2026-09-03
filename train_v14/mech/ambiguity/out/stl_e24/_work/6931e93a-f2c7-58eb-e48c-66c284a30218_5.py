from build123d import *

block_length = 80.0
block_width = 60.0
block_height = 20.0
corner_fillet_radius = 5.0
edge_chamfer = 2.0
pocket_length = 40.0
pocket_width = 30.0
pocket_depth = 5.0
hole_diameter = 2.0
hole_spacing_x = 6.0
hole_spacing_y = 6.0
hole_margin = 8.0
boss_diameter = 20.0
boss_height = 5.0

with BuildPart() as p:
    with BuildSketch() as s:
        Rectangle(block_length, block_width)
    extrude(amount=block_height)

solid_body = p.part

top_edges = solid_body.edges().filter_by(Axis.Z).sort_by(Axis.Z)[-1:]
solid_body = fillet(top_edges, corner_fillet_radius)

vert_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = chamfer(vert_edges, edge_chamfer)

pocket = Pos(0, 0, block_height - pocket_depth/2) * Box(pocket_length, pocket_width, pocket_depth)
solid_body = solid_body - pocket

boss = Pos(0, 0, block_height - pocket_depth + boss_height/2) * Cylinder(boss_diameter/2, boss_height)
solid_body = solid_body + boss

cols = int((block_length - 2 * hole_margin) // hole_spacing_x) + 1
rows = int((block_width - 2 * hole_margin) // hole_spacing_y) + 1
start_x = -block_length / 2 + hole_margin
start_y = -block_width / 2 + hole_margin

for i in range(cols):
    for j in range(rows):
        x = start_x + i * hole_spacing_x
        y = start_y + j * hole_spacing_y
        hole = Pos(x, y, block_height/2) * Cylinder(hole_diameter/2, block_height + 10)
        solid_body = solid_body - hole

part = solid_body
part.name = "block_with_pocket_boss_and_holes"
export_step(part, "output.step")