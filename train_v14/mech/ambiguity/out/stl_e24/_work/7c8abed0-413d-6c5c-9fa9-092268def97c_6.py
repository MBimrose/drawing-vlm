from build123d import *

block_length = 80.0
block_width = 30.0
block_height = 20.0
pocket_length = 40.0
pocket_width = 20.0
pocket_depth = 10.0
hole_diameter = 9.0
hole_spacing = 25.0
chamfer_distance = 2.0
rib_thickness = 2.0
rib_height = 5.0
rib_spacing = 20.0

solid_body = Box(block_length, block_width, block_height)

rib1 = Pos(0, -block_width/2 + rib_thickness/2 + 5, block_height/2 + rib_height/2) * Box(rib_thickness, rib_thickness, rib_height)
rib2 = Pos(0, block_width/2 - rib_thickness/2 - 5, block_height/2 + rib_height/2) * Box(rib_thickness, rib_thickness, rib_height)
solid_body = solid_body + rib1 + rib2

pocket = Pos(0, 0, block_height - pocket_depth/2) * Box(pocket_length, pocket_width, pocket_depth)
solid_body = solid_body - pocket

for x in [-hole_spacing, 0, hole_spacing]:
    hole = Pos(x, 0, 0) * Rot(90, 0, 0) * Cylinder(hole_diameter/2, block_width + 10)
    solid_body = solid_body - hole

rear_edges = solid_body.edges().filter_by(Axis.Z).sort_by(Axis.Y)[:2]
solid_body = chamfer(rear_edges, chamfer_distance)

part = solid_body
part.name = "ribbed_block_with_pocket_and_holes"
export_step(part, "output.step")