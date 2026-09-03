from build123d import *

block_length = 80.0
block_width = 60.0
block_thickness = 15.0
slot_length = 30.0
slot_width = 10.0
pocket_margin = 5.0
pocket_depth = 4.0
hole_diameter = 5.0
hole_offset_x = 20.0
hole_offset_y = 15.0

solid_body = Box(block_length, block_width, block_thickness)
solid_body = solid_body - Box(slot_length, slot_width, block_thickness)

pocket_w = block_length - 2 * pocket_margin
pocket_h = block_width - 2 * pocket_margin
pocket_z = block_thickness / 2 - pocket_depth / 2
solid_body = solid_body - Pos(0, 0, pocket_z) * Box(pocket_w, pocket_h, pocket_depth)

hole_r = hole_diameter / 2
for x, y in [(-hole_offset_x, -hole_offset_y), (hole_offset_x, -hole_offset_y),
             (-hole_offset_x, hole_offset_y), (hole_offset_x, hole_offset_y)]:
    solid_body = solid_body - Pos(x, y, 0) * Cylinder(hole_r, block_thickness)

part = solid_body
part.name = "block_with_slot_pocket_holes"
export_step(part, "output.step")