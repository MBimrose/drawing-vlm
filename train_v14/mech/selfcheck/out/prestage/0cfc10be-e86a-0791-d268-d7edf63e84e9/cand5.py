from build123d import *

base_radius = 30.0
base_height = 20.0
arm_length = 60.0
arm_width = 25.0
arm_thickness = 8.0
arm_offset = 10.0
hole_diameter = 6.0
cbore_diameter = 10.0
cbore_depth = 4.0
chamfer_size = 1.0

base = Cylinder(base_radius, base_height)
arm = Pos(arm_offset, arm_width/2, base_height) * Box(arm_thickness, arm_width, arm_length)
result = base + arm

shaft_hole = Cylinder(hole_diameter/2, base_height + arm_length)
cbore_hole = Pos(0, 0, base_height - cbore_depth) * Cylinder(cbore_diameter/2, cbore_depth)
result = result - shaft_hole - cbore_hole

vertical_edges = result.edges().filter_by(Axis.Z)
result = chamfer(vertical_edges, chamfer_size)

part = result
part.name = "base_with_arm_and_holes"
export_step(part, "output.step")