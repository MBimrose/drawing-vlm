from build123d import *

arm_length = 80.0
arm_width = 15.0
arm_thickness = 5.0
rib_height = 2.0
rib_width = arm_width * 0.8
groove_width = arm_width * 0.6
groove_depth = 2.0
groove_margin = 5.0
hole_diameter = 5.0
hole_spacing = 20.0
chamfer_size = 0.5
mount_hole_diameter = 3.0
mount_hole_offset = 2.0

base = Box(arm_width, arm_thickness, arm_length)
base = chamfer(base.edges().filter_by(Axis.Z), chamfer_size)

rib = Pos(0, arm_thickness/2 + rib_height/2, 0) * Box(rib_width, rib_height, arm_length)
result = base + rib

groove = Pos(0, -arm_thickness/2 + groove_depth/2, 0) * Box(groove_width, groove_depth, arm_length - 2*groove_margin)
result = result - groove

for x, z in [(-hole_spacing, -hole_spacing), (0, 0), (hole_spacing, hole_spacing)]:
    result = result - Pos(x, 0, z) * Rot(90, 0, 0) * Cylinder(hole_diameter/2, arm_thickness + rib_height + 10)

for x, z in [(arm_width/2, -arm_length/2 + mount_hole_offset), (-arm_width/2, -arm_length/2 + mount_hole_offset),
             (arm_width/2, arm_length/2 - mount_hole_offset), (-arm_width/2, arm_length/2 - mount_hole_offset)]:
    result = result - Pos(x, 0, z) * Rot(0, 90, 0) * Cylinder(mount_hole_diameter/2, arm_width + 10)

part = result
part.name = "arm_with_rib_groove_holes"
export_step(part, "output.step")