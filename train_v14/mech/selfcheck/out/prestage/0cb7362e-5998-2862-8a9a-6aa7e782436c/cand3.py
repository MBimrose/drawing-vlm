from build123d import *

arm_length = 80.0
arm_width = 30.0
arm_thickness = 10.0
rib_height = 6.0
rib_width = 15.0
rib_spacing = 20.0
rib_thickness = 4.0
pocket_length = 40.0
pocket_width = 20.0
pocket_depth = 4.0
hole_diameter = 4.0
cbore_diameter = 7.0
cbore_depth = 2.0
chamfer_size = 1.0

result = Box(arm_length, arm_width, arm_thickness)

rib_count = int((arm_length - rib_spacing) // rib_spacing) + 1
for i in range(rib_count):
    x = (i - (rib_count - 1) / 2) * rib_spacing
    rib = Pos(x, 0, rib_height / 2) * Box(rib_width, rib_thickness, rib_height)
    result = result + rib

pocket = Pos(0, 0, arm_thickness - pocket_depth / 2) * Box(pocket_length, pocket_width, pocket_depth)
result = result - pocket

hole_x = arm_length / 2 - chamfer_size - 5
shaft_hole = Pos(hole_x, 0, 0) * Cylinder(hole_diameter / 2, arm_thickness + 1)
cbore_hole = Pos(hole_x, 0, -arm_thickness / 2 + cbore_depth / 2) * Cylinder(cbore_diameter / 2, cbore_depth)
result = result - shaft_hole - cbore_hole

result = chamfer(result.edges().filter_by(Axis.Z), chamfer_size)

part = result
part.name = "arm_with_ribs_pocket_and_hole"
export_step(part, "output.step")