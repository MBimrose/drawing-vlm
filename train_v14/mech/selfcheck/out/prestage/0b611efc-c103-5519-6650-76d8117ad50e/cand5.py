from build123d import *

vertical_height = 80.0
horizontal_length = 60.0
leg_thickness = 12.0
bracket_thickness = 8.0
pocket_width = 6.0
pocket_height = 10.0
pocket_depth = 7.0
pocket_offset_x = 30.0
pocket_offset_y = 4.0

vertical = Pos(0, 0, bracket_thickness/2) * Box(leg_thickness, vertical_height, bracket_thickness)
horizontal = Pos(horizontal_length/2, vertical_height/2 - leg_thickness/2, bracket_thickness/2) * Box(horizontal_length, leg_thickness, bracket_thickness)
base = vertical + horizontal

pocket = Pos(pocket_offset_x, vertical_height/2 - leg_thickness/2 + pocket_offset_y, bracket_thickness - pocket_depth/2) * Box(pocket_width, pocket_height, pocket_depth)
part = base - pocket
part.name = "L_Bracket"
export_step(part, "output.step")