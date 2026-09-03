from build123d import *

block_width = 80.0
block_depth = 60.0
block_height = 20.0
corner_fillet_radius = 5.0
edge_chamfer = 2.0
boss_diameter = 20.0
boss_height = 10.0
boss_offset_x = 15.0
boss_offset_y = 0.0
pocket_width = 40.0
pocket_depth = 30.0
pocket_depth_z = 5.0
hole_diameter = 2.0
hole_spacing = 6.0
hole_margin = 8.0

with BuildPart() as p:
    with BuildSketch() as s:
        Rectangle(block_width, block_depth)
    extrude(amount=block_height)

solid_body = p.part

top_edges = solid_body.edges().filter_by(Axis.Z).sort_by(Axis.Z)[-1:]
solid_body = fillet(top_edges, corner_fillet_radius)

vert_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = chamfer(vert_edges, edge_chamfer)

boss = Pos(boss_offset_x, boss_offset_y, block_height - boss_height/2) * Cylinder(boss_diameter/2, boss_height)
solid_body = solid_body + boss

pocket = Pos(0, 0, block_height - pocket_depth_z/2) * Box(pocket_width, pocket_depth, pocket_depth_z)
solid_body = solid_body - pocket

num_x = int((block_width - 2 * hole_margin) // hole_spacing) + 1
num_y = int((block_depth - 2 * hole_margin) // hole_spacing) + 1
for i in range(num_x):
    for j in range(num_y):
        x = -block_width/2 + hole_margin + i * hole_spacing
        y = -block_depth/2 + hole_margin + j * hole_spacing
        hole = Pos(x, y, block_height/2) * Cylinder(hole_diameter/2, block_height + 1)
        solid_body = solid_body - hole

part = solid_body
part.name = "block_with_boss_pocket_and_holes"
export_step(part, "output.step")