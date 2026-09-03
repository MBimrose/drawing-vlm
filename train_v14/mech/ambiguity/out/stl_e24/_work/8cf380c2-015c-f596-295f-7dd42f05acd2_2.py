from build123d import *

arm_length = 80.0
arm_width = 30.0
arm_thickness = 10.0
slot_width = 8.0
slot_height = 12.0
rib_width = 6.0
rib_height = 4.0
rib_length = 50.0
pocket_width = 15.0
pocket_height = 10.0
pocket_depth = 3.0
pocket_offset_y = 5.0
blind_hole_diameter = 5.0
blind_hole_depth = 8.0
blind_hole_offset_x = 20.0
chamfer_size = 0.8
bottom_pocket_width = 4.0
bottom_pocket_depth = 5.0
bottom_pocket_offset_y = -8.0

result = Box(arm_length, arm_width, arm_thickness)
result = chamfer(result.edges().filter_by(Axis.Z), chamfer_size)
result = result - Box(slot_width, arm_thickness, slot_height)
result = result - Pos(0, pocket_offset_y, arm_thickness/2 - pocket_depth/2) * Box(pocket_width, pocket_height, pocket_depth)
result = result - Pos(blind_hole_offset_x - arm_length/2, 0, arm_thickness/2 - blind_hole_depth/2) * Cylinder(blind_hole_diameter/2, blind_hole_depth)
result = result + Pos(0, 0, arm_thickness/2 + rib_height/2) * Box(rib_length, rib_width, rib_height)
result = result - Pos(0, bottom_pocket_offset_y, 0) * Box(arm_length - 2*rib_length/2, bottom_pocket_width, bottom_pocket_depth)

part = result
part.name = "arm_with_features"
export_step(part, "output.step")