from build123d import *

block_length = 80.0
block_width = 60.0
block_thickness = 15.0
pocket_depth = 4.0
pocket_margin = 5.0
slot_length = 30.0
slot_width = 10.0
hole_diameter = 5.0
hole_spacing_x = 40.0
hole_spacing_y = 30.0

solid_body = Box(block_length, block_width, block_thickness)

pocket_w = block_length - 2 * pocket_margin
pocket_h = block_width - 2 * pocket_margin
pocket_box = Pos(0, 0, block_thickness/2 - pocket_depth/2) * Box(pocket_w, pocket_h, pocket_depth)
solid_body = solid_body - pocket_box

slot_box = Box(slot_length, slot_width, block_thickness)
solid_body = solid_body - slot_box

hole_r = hole_diameter / 2
for x in [-hole_spacing_x/2, hole_spacing_x/2]:
    for y in [-hole_spacing_y/2, hole_spacing_y/2]:
        hole = Pos(x, y, 0) * Cylinder(hole_r, block_thickness)
        solid_body = solid_body - hole

part = solid_body
part.name = "block_with_pocket_slot_holes"
export_step(part, "output.step")