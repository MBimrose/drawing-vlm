from build123d import *

leg_length_long = 80.0
leg_length_short = 50.0
leg_width = 20.0
thickness = 8.0
fillet_radius = 2.0
pocket_width = 12.0
pocket_depth = 6.0
pocket_height = 30.0
counterbore_diameter = 10.0
counterbore_depth = 4.0
through_hole_diameter = 6.0
through_hole_offset = 35.0
pattern_hole_diameter = 4.0
pattern_hole_count = 4
pattern_hole_spacing = (leg_length_long - 2 * leg_width) / (pattern_hole_count + 1)

leg_long = Pos(leg_length_long/2, leg_width/2, thickness/2) * Box(leg_length_long, leg_width, thickness)
leg_short = Pos(leg_width/2, leg_width + leg_length_short/2, thickness/2) * Box(leg_width, leg_length_short, thickness)
result = leg_long + leg_short
result = fillet(result.edges(), fillet_radius)

pocket = Pos(leg_width - pocket_width/2, leg_width + pocket_height/2, thickness/2) * Box(pocket_width, pocket_height, pocket_depth)
result = result - pocket

cbore = Pos(0, through_hole_offset, thickness/2) * Rot(0, 90, 0) * Cylinder(counterbore_diameter/2, counterbore_depth)
result = result - cbore

thru = Pos(0, through_hole_offset, thickness/2) * Rot(0, 90, 0) * Cylinder(through_hole_diameter/2, thickness + 2)
result = result - thru

for i in range(pattern_hole_count):
    x = leg_width + pattern_hole_spacing * (i + 1)
    y = leg_width / 2
    hole = Pos(x, y, thickness/2) * Cylinder(pattern_hole_diameter/2, thickness + 2)
    result = result - hole

part = result
part.name = "L_bracket"
export_step(part, "output.step")