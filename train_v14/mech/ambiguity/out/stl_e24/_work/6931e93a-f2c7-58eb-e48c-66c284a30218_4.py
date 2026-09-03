from build123d import *

block_length = 80.0
block_width = 60.0
block_height = 20.0
corner_fillet_radius = 5.0
chamfer_distance = 2.0
pocket_length = 40.0
pocket_width = 30.0
pocket_depth = 5.0
hole_diameter = 2.0
hole_spacing = 6.0
hole_rows = 8
hole_cols = 11

with BuildPart() as p:
    with BuildSketch() as s:
        Rectangle(block_length, block_width)
    extrude(amount=block_height)

solid_body = p.part

vertical_edges = solid_body.edges().filter_by(Axis.Z)
top_right_edge = max(vertical_edges, key=lambda e: (e.center().X, e.center().Y))
solid_body = fillet([top_right_edge], corner_fillet_radius)

vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = chamfer(vertical_edges, chamfer_distance)

pocket = Pos(0, 0, block_height - pocket_depth/2) * Box(pocket_length, pocket_width, pocket_depth)
solid_body = solid_body - pocket

for i in range(hole_cols):
    for j in range(hole_rows):
        x = (i - (hole_cols - 1) / 2) * hole_spacing
        y = (j - (hole_rows - 1) / 2) * hole_spacing
        hole = Pos(x, y, block_height/2) * Cylinder(hole_diameter/2, block_height + 10)
        solid_body = solid_body - hole

part = solid_body
part.name = "block_with_pocket_and_holes"
export_step(part, "output.step")