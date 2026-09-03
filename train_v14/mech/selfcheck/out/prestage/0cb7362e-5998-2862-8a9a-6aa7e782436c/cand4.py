from build123d import *

arm_length = 80.0
arm_width = 30.0
arm_thickness = 10.0
groove_width = 12.0
groove_depth = 4.0
groove_margin = 10.0
groove_length = arm_length - 2 * groove_margin
rib_height = 2.0
rib_width = 6.0
rib_spacing = 12.0
rib_count = int((arm_length - 2 * groove_margin) // rib_spacing)
set_screw_diameter = 4.0
set_screw_head_diameter = 7.0
set_screw_head_depth = 2.0
set_screw_offset = 4.0
chamfer_size = 1.0

result = Box(arm_length, arm_width, arm_thickness)

groove = Pos(0, 0, arm_thickness - groove_depth / 2) * Box(groove_length, groove_width, groove_depth)
result = result - groove

for i in range(rib_count):
    x = (i - (rib_count - 1) / 2) * rib_spacing
    rib = Pos(x, 0, rib_height / 2) * Box(rib_width, arm_width - 2 * groove_margin, rib_height)
    result = result + rib

hole_x = arm_length / 2 - set_screw_offset
shaft_hole = Pos(hole_x, 0, 0) * Cylinder(set_screw_diameter / 2, arm_thickness + 1)
result = result - shaft_hole
cbore_hole = Pos(hole_x, 0, -arm_thickness / 2 + set_screw_head_depth / 2) * Cylinder(set_screw_head_diameter / 2, set_screw_head_depth)
result = result - cbore_hole

vertical_edges = result.edges().filter_by(Axis.Z)
result = chamfer(vertical_edges, chamfer_size)

part = result
part.name = "arm_with_groove_ribs"
export_step(part, "output.step")