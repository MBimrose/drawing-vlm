from build123d import *
import math

block_length = 80.0
block_width = 60.0
block_thickness = 12.0
pocket_diameter = 30.0
pocket_depth = 6.0
rib_width = 10.0
rib_height = 8.0
rib_thickness = 4.0
hole_diameter = 5.0
countersink_diameter = 10.0
countersink_angle = 82.0
hole_offset = 15.0
chamfer_distance = 1.0

solid_body = Box(block_length, block_width, block_thickness)
solid_body = solid_body - Pos(0, 0, block_thickness/2 - pocket_depth/2) * Cylinder(pocket_diameter/2, pocket_depth)
solid_body = solid_body + Pos(0, 0, block_thickness/2 - rib_thickness/2) * Box(rib_width, rib_height, rib_thickness)

csk_depth = (countersink_diameter/2 - hole_diameter/2) / math.tan(math.radians(countersink_angle/2))
hole_positions = [
    (-block_length/2 + hole_offset, -block_width/2 + hole_offset),
    ( block_length/2 - hole_offset, -block_width/2 + hole_offset),
    ( block_length/2 - hole_offset,  block_width/2 - hole_offset),
    (-block_length/2 + hole_offset,  block_width/2 - hole_offset),
]
for x, y in hole_positions:
    solid_body = solid_body - Pos(x, y, 0) * Cylinder(hole_diameter/2, block_thickness)
    solid_body = solid_body - Pos(x, y, block_thickness/2 - csk_depth/2) * Cone(hole_diameter/2, countersink_diameter/2, csk_depth)

solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_distance)

part = solid_body
part.name = "block_with_pocket_rib_holes"
export_step(part, "output.step")