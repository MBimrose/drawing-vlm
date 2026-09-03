from build123d import *

arm_length = 80.0
arm_width = 20.0
arm_thickness = 10.0
flange_length = 40.0
flange_width = 30.0
flange_thickness = arm_thickness
hinge_hole_diameter = 10.0
mount_hole_diameter = 6.0
mount_hole_spacing = 20.0
rib_cut_depth = 5.0
rib_width = arm_width
pocket_length = 50.0
pocket_width = 8.0
pocket_depth = 4.0
chamfer_size = 0.8

base = Box(arm_length, arm_width, arm_thickness)
flange = Pos(-(arm_length/2 + flange_length/2), 0, 0) * Box(flange_length, flange_width, flange_thickness)
result = base + flange

hinge_x = arm_length/2 - hinge_hole_diameter/2 - 2
result = result - Pos(hinge_x, 0, 0) * Cylinder(hinge_hole_diameter/2, arm_thickness * 2)

mount_x1 = -(arm_length/2 + flange_length/2) + mount_hole_spacing/2
mount_x2 = mount_x1 + mount_hole_spacing
result = result - Pos(mount_x1, 0, 0) * Cylinder(mount_hole_diameter/2, arm_thickness * 2)
result = result - Pos(mount_x2, 0, 0) * Cylinder(mount_hole_diameter/2, arm_thickness * 2)

rib_cut = Pos(0, arm_width/2 + rib_cut_depth/2, 0) * Box(arm_length, rib_cut_depth, rib_width)
result = result - rib_cut
rib_cut2 = Pos(0, -(arm_width/2 + rib_cut_depth/2), 0) * Box(arm_length, rib_cut_depth, rib_width)
result = result - rib_cut2

pocket = Pos(0, 0, arm_thickness/2 - pocket_depth/2) * Box(pocket_length, pocket_width, pocket_depth)
result = result - pocket

result = chamfer(result.edges().filter_by(Axis.Z), chamfer_size)

part = result
part.name = "arm_with_flange"
export_step(part, "output.step")