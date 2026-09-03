from build123d import *

vertical_height = 80.0
horizontal_length = 60.0
leg_thickness = 12.0
bracket_thickness = 8.0
slot_width = 6.0
slot_length = 30.0
slot_depth = bracket_thickness - 1.0

vertical = Box(leg_thickness, vertical_height, bracket_thickness)
horizontal = Pos(leg_thickness/2 + horizontal_length/2, vertical_height/2 - leg_thickness/2, 0) * Box(horizontal_length, leg_thickness, bracket_thickness)
base = vertical + horizontal

slot = Pos(leg_thickness/2 + horizontal_length/2, vertical_height/2 - leg_thickness/2, bracket_thickness/2 - slot_depth/2) * Box(slot_width, slot_length, slot_depth)
part = base - slot
part.name = "L_Bracket"
export_step(part, "output.step")