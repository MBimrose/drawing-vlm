from build123d import *

jaw_length = 80.0
jaw_width = 30.0
jaw_thickness = 10.0
notch_width = 8.0
notch_depth = 10.0
pocket_width = 12.0
pocket_depth = 6.0
boss_radius = 5.0
boss_height = 4.0
hole_diameter = 4.0
countersink_diameter = 6.0
countersink_depth = 2.0
hole_spacing = 18.0
hole_count = 3
chamfer_size = 0.5

result = Box(jaw_length, jaw_width, jaw_thickness)

notch = Pos(-jaw_length/4, -jaw_width/2 + notch_depth/2, 0) * Box(notch_width, notch_depth, jaw_thickness)
result = result - notch

pocket = Pos(jaw_length/2 - pocket_width/2, jaw_width/2 - pocket_depth/2, 0) * Box(pocket_width, pocket_depth, jaw_thickness)
result = result - pocket

boss = Pos(0, 0, jaw_thickness/2 + boss_height/2) * Cylinder(boss_radius, boss_height)
result = result + boss

for i in range(hole_count):
    x = (i - (hole_count - 1) / 2) * hole_spacing
    shaft = Pos(x, 0, 0) * Cylinder(hole_diameter/2, jaw_thickness)
    result = result - shaft
    csink = Pos(x, 0, jaw_thickness/2 - countersink_depth/2) * Cone(hole_diameter/2, countersink_diameter/2, countersink_depth)
    result = result - csink

result = chamfer(result.edges().filter_by(Axis.Z), chamfer_size)

part = result
part.name = "jaw_plate"
export_step(part, "output.step")