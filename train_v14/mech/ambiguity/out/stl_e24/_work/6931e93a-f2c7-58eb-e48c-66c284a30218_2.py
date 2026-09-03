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
rib_thickness = 4.0
rib_height = 10.0

solid_body = Box(block_length, block_width, block_height)

vertical_edges = solid_body.edges().filter_by(Axis.Z)
target_edge = max(vertical_edges, key=lambda e: (e.center().X, e.center().Y))
solid_body = fillet([target_edge], corner_fillet_radius)

vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = chamfer(vertical_edges, edge_chamfer)

pocket = Pos(0, 0, block_height/2 - pocket_depth/2) * Box(pocket_length, pocket_width, pocket_depth)
solid_body = solid_body - pocket

rib = Pos(0, 0, block_height/2 - rib_height/2) * Box(rib_thickness, rib_height, rib_height)
solid_body = solid_body + rib

cols = int((block_length - 2 * hole_margin) // hole_spacing_x) + 1
rows = int((block_width - 2 * hole_margin) // hole_spacing_y) + 1
x_start = -block_length / 2 + hole_margin
y_start = -block_width / 2 + hole_margin

for i in range(cols):
    for j in range(rows):
        x = x_start + i * hole_spacing_x
        y = y_start + j * hole_spacing_y
        hole = Pos(x, y, 0) * Cylinder(hole_diameter/2, block_height * 2)
        solid_body = solid_body - hole

part = solid_body
part.name = "block_with_pocket_rib_and_holes"
export_step(part, "output.step")