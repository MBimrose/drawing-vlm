from build123d import *

arm_length = 80.0
arm_width = 20.0
arm_thickness = 10.0
flange_length = 40.0
flange_width = 30.0
flange_thickness = arm_thickness
overlap = 20.0
slot_width = 10.0
slot_depth = 8.0
slot_length = 60.0
clearance_hole_diameter = 10.0
mount_hole_diameter = 6.0
mount_hole_spacing = 20.0
chamfer_size = 0.5

arm = Pos(arm_length/2, 0, 0) * Box(arm_length, arm_width, arm_thickness)
flange = Pos(-flange_length/2 + overlap, 0, 0) * Box(flange_length, flange_width, flange_thickness)
base = arm + flange

slot = Pos(arm_length/2 - slot_length/2, 0, arm_thickness - slot_depth/2) * Box(slot_length, slot_width, slot_depth)
base = base - slot

clearance_hole = Pos(arm_length - arm_width/2, 0, 0) * Cylinder(clearance_hole_diameter/2, arm_thickness)
base = base - clearance_hole

for x in [-flange_length/2 + overlap - mount_hole_spacing/2, -flange_length/2 + overlap + mount_hole_spacing/2]:
    base = base - Pos(x, 0, 0) * Cylinder(mount_hole_diameter/2, arm_thickness)

base = chamfer(base.edges().filter_by(Axis.Z), chamfer_size)

part = base
part.name = "arm_with_flange"
export_step(part, "output.step")