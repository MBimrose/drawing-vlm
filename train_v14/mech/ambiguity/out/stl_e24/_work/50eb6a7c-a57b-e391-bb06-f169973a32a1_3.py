from build123d import *

block_length = 70
block_width = 40
block_height = 12
fillet_radius = 4
chamfer_distance = 0.8
hole_diameter = 6
hole_depth = 8
hole_spacing = block_length / 4
pocket_width = 10
pocket_height = 8
pocket_depth = 8
rib_width = 6
rib_height = 4
rib_thickness = 2

solid_body = Box(block_length, block_width, block_height)

vertical_edges = solid_body.edges().filter_by(Axis.Z).sort_by(Axis.Y)[-2:]
solid_body = fillet(vertical_edges, fillet_radius)

bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
bottom_edges = bottom_face.edges()
solid_body = chamfer(bottom_edges, chamfer_distance)

pocket = Pos(block_length/2 - pocket_depth/2, 0, 0) * Box(pocket_depth, pocket_width, pocket_height)
solid_body = solid_body - pocket

for x in [-hole_spacing, 0, hole_spacing]:
    hole = Pos(x, 0, block_height/2 - hole_depth/2) * Cylinder(hole_diameter/2, hole_depth)
    solid_body = solid_body - hole

rib = Pos(-block_length/2 + rib_width/2 + 5, 0, rib_thickness/2) * Box(rib_width, rib_height, rib_thickness)
solid_body = solid_body + rib

part = solid_body
part.name = "block_with_features"
export_step(part, "output.step")