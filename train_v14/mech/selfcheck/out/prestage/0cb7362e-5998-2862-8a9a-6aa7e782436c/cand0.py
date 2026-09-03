from build123d import *

arm_length = 80.0
arm_width = 30.0
arm_thickness = 10.0
groove_width = 12.0
groove_depth = 4.0
groove_length = 60.0
set_screw_diameter = 4.0
set_screw_head_diameter = 7.0
set_screw_head_depth = 2.0
set_screw_offset_from_end = 4.0
chamfer_size = 1.0
rib_height = 2.0
rib_width = 6.0
rib_spacing = 15.0

solid_body = Box(arm_length, arm_width, arm_thickness)

groove = Pos(0, 0, arm_thickness - groove_depth/2) * Box(groove_length, groove_width, groove_depth)
solid_body = solid_body - groove

hole_x = arm_length/2 - set_screw_offset_from_end
cbore = Pos(hole_x, 0, arm_thickness/2 - set_screw_head_depth/2) * Cylinder(set_screw_head_diameter/2, set_screw_head_depth)
shaft = Pos(hole_x, 0, 0) * Cylinder(set_screw_diameter/2, arm_thickness + 1)
solid_body = solid_body - cbore - shaft

solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_size)

rib_count = int((arm_length - 2 * rib_spacing) // rib_spacing) + 1
for i in range(rib_count):
    x_pos = -arm_length/2 + rib_spacing + i * rib_spacing
    rib = Pos(x_pos, 0, rib_height/2) * Box(rib_width, arm_width - 4, rib_height)
    solid_body = solid_body + rib

part = solid_body
part.name = "arm_with_groove_and_ribs"
export_step(part, "output.step")