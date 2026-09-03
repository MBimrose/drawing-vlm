from build123d import *

leaf_length = 80.0
leaf_width = 30.0
leaf_thickness = 6.0
notch_width = 6.0
notch_depth = 8.0
notch_offset = 12.0
slot_width = 4.0
slot_length = 20.0
slot_offset = 5.0
hole_diameter = 4.0
hole_spacing_x = 20.0
hole_spacing_y = 10.0
hole_rows = 2
hole_cols = 4
hole_margin = 10.0

solid_body = Box(leaf_length, leaf_width, leaf_thickness)

notch_x = -leaf_length/2 + notch_offset + notch_width/2
notch = Pos(notch_x, 0, 0) * Box(notch_width, notch_depth, leaf_thickness)
solid_body = solid_body - notch

slot_x = leaf_length/2 - slot_width/2
slot = Pos(slot_x, 0, 0) * Box(slot_width, slot_length, leaf_thickness)
solid_body = solid_body - slot

for i in range(hole_cols):
    for j in range(hole_rows):
        x = -leaf_length/2 + hole_margin + i * hole_spacing_x
        y = -leaf_width/2 + hole_margin + j * hole_spacing_y
        hole = Pos(x, y, 0) * Cylinder(hole_diameter/2, leaf_thickness)
        solid_body = solid_body - hole

part = solid_body
part.name = "leaf_with_notch_slot_holes"
export_step(part, "output.step")