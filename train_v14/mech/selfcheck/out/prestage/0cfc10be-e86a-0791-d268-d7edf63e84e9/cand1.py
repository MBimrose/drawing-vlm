from build123d import *

knob_outer_radius = 30.0
knob_height = 20.0
arm_width = 25.0
arm_thickness = 8.0
arm_length = 40.0
central_hole_diameter = 6.0
counterbore_diameter = 10.0
counterbore_depth = 4.0

base = Cylinder(knob_outer_radius, knob_height)
arm = Pos(arm_thickness/2, arm_width/2, knob_height/2 + arm_length/2) * Box(arm_thickness, arm_width, arm_length)
result = base + arm
result = result - Cylinder(central_hole_diameter/2, knob_height)
result = result - Pos(0, 0, knob_height/2 - counterbore_depth/2) * Cylinder(counterbore_diameter/2, counterbore_depth)

part = result
part.name = "knob_with_arm"
export_step(part, "output.step")