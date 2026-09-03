from build123d import *

leg_a = 60.0
leg_b = 50.0
thickness = 8.0
leg_width = 10.0
fillet_radius = 3.0
hole_diameter = 22.0
notch_width = 12.0
notch_depth = 15.0
notch_offset = 20.0

vertical = Pos(leg_width/2, leg_b/2, thickness/2) * Box(leg_width, leg_b, thickness)
horizontal = Pos(leg_a/2, leg_width/2, thickness/2) * Box(leg_a, leg_width, thickness)
result = vertical + horizontal

notch = Pos(leg_width + notch_width/2, notch_offset + notch_depth/2, thickness/2) * Box(notch_width, notch_depth, thickness)
result = result - notch

result = fillet(result.edges().filter_by(Axis.Z), fillet_radius)

result = result - Pos(leg_width, leg_width, thickness/2) * Cylinder(hole_diameter/2, thickness * 2)

part = result
part.name = "L_Bracket"
export_step(part, "output.step")