from build123d import *

block_width = 80.0
block_depth = 60.0
block_height = 20.0
corner_fillet_radius = 5.0
chamfer_distance = 2.0
pocket_width = 40.0
pocket_depth = 40.0
pocket_height = 5.0
hole_diameter = 2.0
hole_spacing_x = 6.0
hole_spacing_y = 6.0
hole_rows = 8
hole_cols = 11

solid = Box(block_width, block_depth, block_height)

vertical_edges = solid.edges().filter_by(Axis.Z)
target_edge = max(vertical_edges, key=lambda e: (e.center().X, e.center().Y))
solid = fillet([target_edge], corner_fillet_radius)

solid = chamfer(solid.edges().filter_by(Axis.Z), chamfer_distance)

pocket = Pos(0, 0, block_height/2 - pocket_height/2) * Box(pocket_width, pocket_depth, pocket_height)
solid = solid - pocket

for i in range(hole_cols):
    for j in range(hole_rows):
        x = (i - (hole_cols - 1) / 2) * hole_spacing_x
        y = (j - (hole_rows - 1) / 2) * hole_spacing_y
        hole = Pos(x, y, 0) * Cylinder(hole_diameter/2, block_height + 10)
        solid = solid - hole

part = solid
part.name = "filleted_chamfered_block_with_pocket_and_holes"
export_step(part, "output.step")