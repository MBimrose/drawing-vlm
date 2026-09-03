from build123d import *

arm_length = 80.0
arm_width = 20.0
arm_thickness = 10.0
rib_length = 30.0
rib_width = 6.0
rib_height = 10.0
rib_offset_from_end = 5.0
hole_diameter = 4.0
hole_spacing = 15.0
hole_count = 4
hole_start_offset = 25.0
notch_width = 4.0
notch_depth = 3.0

base = Box(arm_length, arm_width, arm_thickness)
rib = Pos(arm_length/2 - rib_offset_from_end - rib_length/2, arm_width/2 + rib_width/2, rib_height/2) * Box(rib_length, rib_width, rib_height)
result = base + rib

notch = Pos(arm_length/2 - rib_offset_from_end - rib_length/2, arm_width/2 + rib_width/2, rib_height - notch_depth/2) * Box(notch_width, notch_width, notch_depth)
result = result - notch

for i in range(hole_count):
    x = hole_start_offset + i * hole_spacing
    result = result - Pos(x, 0, arm_thickness/2) * Cylinder(hole_diameter/2, arm_thickness)

part = result
part.name = "arm_with_rib"
export_step(part, "output.step")