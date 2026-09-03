from build123d import *

leg_width = 12.0
vertical_height = 80.0
horizontal_length = 52.0
thickness = 8.0
slot_width = 6.0
slot_length = 30.0
slot_depth = thickness - 1.0

vertical = Box(leg_width, vertical_height, thickness)
horizontal = Pos(leg_width/2 + horizontal_length/2, vertical_height/2 - leg_width/2, 0) * Box(horizontal_length, leg_width, thickness)
base = vertical + horizontal

slot_center_x = leg_width/2 + horizontal_length/2
slot_center_y = vertical_height/2 - leg_width/2
slot = Pos(slot_center_x, slot_center_y, thickness/2 - slot_depth/2) * Box(slot_width, slot_length, slot_depth)
result = base - slot

part = result
part.name = "L_Bracket"
export_step(part, "output.step")