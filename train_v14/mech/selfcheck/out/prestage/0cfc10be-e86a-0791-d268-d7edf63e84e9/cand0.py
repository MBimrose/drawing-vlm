from build123d import *

knob_outer_radius = 30.0
knob_height = 20.0
rib_width = 8.0
rib_length = 25.0
rib_height = 40.0
central_hole_diameter = 6.0
counterbore_diameter = 10.0
counterbore_depth = 4.0

base = Cylinder(knob_outer_radius, knob_height)
rib = Pos(0, rib_length/2, knob_height/2 + rib_height/2) * Box(rib_width, rib_length, rib_height)
result = base + rib

shaft_hole = Cylinder(central_hole_diameter/2, knob_height + rib_height + 10)
cbore_hole = Pos(0, 0, knob_height/2 - counterbore_depth/2) * Cylinder(counterbore_diameter/2, counterbore_depth)
result = result - shaft_hole - cbore_hole

part = result
part.name = "knob_with_rib"
export_step(part, "output.step")