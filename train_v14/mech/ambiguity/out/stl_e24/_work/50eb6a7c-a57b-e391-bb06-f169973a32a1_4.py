from build123d import *

block_length = 70.0
block_width = 40.0
block_height = 12.0
fillet_radius = 4.0
chamfer_distance = 0.8
hole_diameter = 6.0
hole_depth = 8.0
hole_spacing = block_length / 4.0
tab_width = 10.0
tab_height = 6.0
pocket_width = 10.0
pocket_height = 8.0
pocket_depth = 8.0

solid_body = Box(block_length, block_width, block_height)
tab = Pos(block_length/2 - tab_width/2, 0, 0) * Box(tab_width, tab_height, block_height)
solid_body = solid_body + tab

vertical_edges = solid_body.edges().filter_by(Axis.Z)
left_edges = vertical_edges.sort_by(Axis.X)[:2]
solid_body = fillet(left_edges, fillet_radius)

bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
bottom_edges = bottom_face.edges()
solid_body = chamfer(bottom_edges, chamfer_distance)

for x, y in [(-hole_spacing, 0), (0, 0), (hole_spacing, 0)]:
    solid_body = solid_body - Pos(x, y, block_height/2 - hole_depth/2) * Cylinder(hole_diameter/2, hole_depth)

pocket = Pos(block_length/2 - pocket_depth/2, 0, 0) * Box(pocket_depth, pocket_width, pocket_height)
solid_body = solid_body - pocket

part = solid_body
part.name = "block_with_tab_holes_pocket"
export_step(part, "output.step")