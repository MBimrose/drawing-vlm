from build123d import *

block_length = 80.0
block_width = 60.0
block_thickness = 10.0
boss_diameter = 30.0
boss_height = 12.0
hole_diameter = 8.0
hole_spacing_x = 30.0
hole_spacing_y = 20.0
hole_rows = 2
hole_cols = 2
chamfer_distance = 1.0
pocket_width = 20.0
pocket_length = 40.0
pocket_depth = 4.0
pocket_offset = 15.0

with BuildPart() as p:
    with BuildSketch() as s:
        Rectangle(block_length, block_width)
    extrude(amount=block_thickness)

solid_body = p.part

for i in range(hole_cols):
    for j in range(hole_rows):
        x = (i - (hole_cols - 1) / 2) * hole_spacing_x
        y = (j - (hole_rows - 1) / 2) * hole_spacing_y
        solid_body = solid_body - Pos(x, y, block_thickness) * Cylinder(hole_diameter / 2, block_thickness + 2)

solid_body = solid_body + Pos(0, 0, block_thickness) * Cylinder(boss_diameter / 2, boss_height)

solid_body = solid_body - Pos(pocket_offset, 0, block_thickness + boss_height - pocket_depth / 2) * Box(pocket_length, pocket_width, pocket_depth)

vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = chamfer(vertical_edges, chamfer_distance)

part = solid_body
part.name = "block_with_boss_and_pocket"
export_step(part, "output.step")