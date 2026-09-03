from build123d import *

block_length = 70.0
block_width = 40.0
block_height = 12.0
fillet_radius = 4.0
chamfer_distance = 0.8
hole_diameter = 6.0
hole_depth = 8.0
hole_spacing = block_length / 4.0
rib_thickness = 3.0
rib_height = 4.0
rib_offset_y = -block_width / 4.0
pocket_width = 10.0
pocket_height = 8.0
pocket_depth = 8.0

solid_body = Box(block_length, block_width, block_height)

front_vertical_edges = solid_body.edges().filter_by(Axis.Z).sort_by(Axis.Y)[-2:]
solid_body = fillet(front_vertical_edges, fillet_radius)

bottom_front_edge = solid_body.edges().filter_by(Axis.X).sort_by(Axis.Z)[:2].sort_by(Axis.Y)[:1]
solid_body = chamfer(bottom_front_edge, chamfer_distance)

for x in [-hole_spacing, 0, hole_spacing]:
    solid_body = solid_body - Pos(x, 0, block_height/2 - hole_depth/2) * Cylinder(hole_diameter/2, hole_depth)

rib = Pos(0, rib_offset_y, block_height/2 - rib_height/2) * Box(rib_thickness, rib_height, rib_height)
solid_body = solid_body + rib

pocket = Pos(block_length/2 - pocket_depth/2, 0, 0) * Box(pocket_depth, pocket_width, pocket_height)
solid_body = solid_body - pocket

part = solid_body
part.name = "block_with_features"
export_step(part, "output.step")