from build123d import *

block_length = 80.0
block_width = 30.0
block_thickness = 10.0
rib_width = 6.0
rib_height = 4.0
rib_length = 50.0
pocket_width = 15.0
pocket_depth = 10.0
pocket_height = 3.0
slot_width = 8.0
slot_height = 12.0
slot_depth = 8.0
hole_diameter = 5.0
hole_depth = 8.0
hole_offset_x = 20.0
hole_offset_y = 0.0
chamfer_size = 0.8
groove_width = 4.0
groove_depth = 5.0
groove_length = 50.0

solid_body = Box(block_length, block_width, block_thickness)
solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_size)

rib = Pos(0, 0, block_thickness/2 + rib_height/2) * Box(rib_length, rib_width, rib_height)
solid_body = solid_body + rib

pocket = Pos(0, 0, block_thickness/2 - pocket_height/2) * Box(pocket_width, pocket_depth, pocket_height)
solid_body = solid_body - pocket

slot = Pos(0, block_width/2 - slot_depth/2, 0) * Box(slot_width, slot_depth, slot_height)
solid_body = solid_body - slot

hole = Pos(hole_offset_x - block_length/2, hole_offset_y, 0) * Cylinder(hole_diameter/2, hole_depth)
solid_body = solid_body - hole

groove = Pos(0, -block_width/2 + groove_depth/2, 0) * Box(groove_length, groove_depth, groove_width)
solid_body = solid_body - groove

part = solid_body
part.name = "chamfered_block_with_features"
export_step(part, "output.step")