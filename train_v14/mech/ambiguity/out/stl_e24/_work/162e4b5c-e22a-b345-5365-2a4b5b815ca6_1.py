from build123d import *

arm_length = 80.0
arm_width = 30.0
arm_thickness = 10.0
bearing_diameter = 20.0
bearing_depth = 8.0
split_slot_width = 0.5
mount_hole_diameter = 4.0
mount_hole_spacing = 15.0
mount_hole_offset = 20.0
chamfer_distance = 1.0
rib_height = 2.0
rib_width = 5.0
rib_length = 30.0

result = Box(arm_length, arm_width, arm_thickness)

bearing_center_x = arm_length / 2 - bearing_diameter / 2
bearing_cut = Pos(bearing_center_x, 0, -arm_thickness/2 + bearing_depth/2) * Cylinder(bearing_diameter/2, bearing_depth)
result = result - bearing_cut

slot_cut = Box(split_slot_width, arm_width, arm_thickness)
result = result - slot_cut

mount_center_x = -arm_length / 2 + mount_hole_offset
for y in [-mount_hole_spacing/2, mount_hole_spacing/2]:
    hole = Pos(mount_center_x, y, 0) * Cylinder(mount_hole_diameter/2, arm_thickness)
    result = result - hole

rib = Pos(0, 0, -arm_thickness/2 + rib_height/2) * Box(rib_length, rib_width, rib_height)
result = result + rib

edges = result.edges().filter_by(Axis.Z).sort_by(Axis.X)[:2]
result = chamfer(edges, chamfer_distance)

part = result
part.name = "split_arm"
export_step(part, "output.step")