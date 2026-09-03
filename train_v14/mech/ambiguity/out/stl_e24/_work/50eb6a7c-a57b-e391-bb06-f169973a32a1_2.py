from build123d import *

block_length = 70.0
block_width = 40.0
block_height = 12.0
pocket_width = 10.0
pocket_height = 8.0
pocket_depth = 8.0
hole_diameter = 6.0
hole_depth = 8.0
fillet_radius = 4.0
chamfer_distance = 0.8
rib_thickness = 2.0
rib_width = 6.0
rib_length = block_length - 10.0

solid_body = Box(block_length, block_width, block_height)

pocket = Pos(block_length/2 - pocket_depth/2, 0, 0) * Box(pocket_depth, pocket_width, pocket_height)
solid_body = solid_body - pocket

hole_spacing = block_length / 4.0
for i in range(3):
    x = (i - 1) * hole_spacing
    hole = Pos(x, 0, block_height/2 - hole_depth/2) * Cylinder(hole_diameter/2, hole_depth)
    solid_body = solid_body - hole

fillet_edges = solid_body.edges().filter_by(Axis.Z).sort_by(Axis.Y)[-2:]
solid_body = fillet(fillet_edges, fillet_radius)

chamfer_edges = solid_body.edges().filter_by(Axis.X).sort_by(Axis.Z)[:2]
solid_body = chamfer(chamfer_edges, chamfer_distance)

rib = Pos(0, 0, -block_height/2 + rib_thickness/2) * Box(rib_length, rib_width, rib_thickness)
solid_body = solid_body + rib

part = solid_body
part.name = "block_with_pocket_holes_rib"
export_step(part, "output.step")