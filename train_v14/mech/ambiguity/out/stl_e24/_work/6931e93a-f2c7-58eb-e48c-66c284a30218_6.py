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
hole_spacing_x = 6.0
hole_spacing_y = 6.0
hole_margin = 8.0

with BuildPart() as p:
    with BuildSketch() as s:
        Rectangle(block_length, block_width)
    extrude(amount=block_height)

solid_body = p.part

vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = chamfer(vertical_edges, chamfer_distance)

top_edges = solid_body.edges().filter_by(Axis.Z).sort_by(Axis.Z)[-1:]
solid_body = fillet(top_edges, corner_fillet_radius)

pocket = Pos(0, 0, block_height - pocket_depth/2) * Box(pocket_length, pocket_width, pocket_depth)
solid_body = solid_body - pocket

cols = int((block_length - 2 * hole_margin) // hole_spacing_x) + 1
rows = int((block_width - 2 * hole_margin) // hole_spacing_y) + 1
start_x = -block_length/2 + hole_margin
start_y = -block_width/2 + hole_margin

for i in range(cols):
    for j in range(rows):
        x = start_x + i * hole_spacing_x
        y = start_y + j * hole_spacing_y
        hole = Pos(x, y, block_height/2) * Cylinder(hole_diameter/2, block_height)
        solid_body = solid_body - hole

part = solid_body
part.name = "perforated_block"
export_step(part, "output.step")