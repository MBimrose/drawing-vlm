from build123d import *

block_length = 80.0
block_width = 30.0
block_thickness = 10.0
rib_length = 50.0
rib_width = 5.0
rib_height = 4.0
pocket_width = 15.0
pocket_depth = 3.0
pocket_offset = 7.0
slot_width = 12.0
slot_height = 8.0
slot_depth = 8.0
hole_diameter = 5.0
hole_depth = 8.0
hole_offset_x = -20.0
chamfer_distance = 0.8
groove_width = 4.0
groove_depth = 5.0
groove_length = 50.0

solid_body = Box(block_length, block_width, block_thickness)
solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_distance)

solid_body = solid_body + Pos(0, 0, block_thickness/2 + rib_height/2) * Box(rib_length, rib_width, rib_height)
solid_body = solid_body - Pos(0, pocket_offset, block_thickness/2 - pocket_depth/2) * Box(pocket_width, block_thickness, pocket_depth)
solid_body = solid_body - Pos(0, block_width/2 - slot_depth/2, 0) * Box(slot_width, slot_depth, slot_height)
solid_body = solid_body - Pos(hole_offset_x, 0, block_thickness/2 - hole_depth/2) * Cylinder(hole_diameter/2, hole_depth)
solid_body = solid_body - Pos(0, -block_width/2 + groove_depth/2, 0) * Box(groove_length, groove_depth, groove_width)

part = solid_body
part.name = "block_with_features"
export_step(part, "output.step")