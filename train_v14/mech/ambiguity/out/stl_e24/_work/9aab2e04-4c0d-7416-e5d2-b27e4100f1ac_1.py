from build123d import *

arm_length = 80.0
arm_width = 15.0
arm_thickness = 5.0
rib_height = 2.0
rib_width = 11.0
hole_diameter = 5.0
hole_spacing = 20.0
hole_count = 3
chamfer_size = 0.5
mount_hole_diameter = 3.0
mount_hole_offset = 2.0

base = Box(arm_width, arm_thickness, arm_length)
base = chamfer(base.edges().filter_by(Axis.Z), chamfer_size)

rib = Pos(0, arm_thickness/2 + rib_height/2, 0) * Box(rib_width, rib_height, arm_length)
result = base + rib

for i in range(hole_count):
    z_pos = -arm_length/2 + hole_spacing + i * hole_spacing
    result = result - Pos(0, 0, z_pos) * Rot(90, 0, 0) * Cylinder(hole_diameter/2, arm_thickness + rib_height + 10)

for z_pos in [-arm_length/2 + mount_hole_offset, arm_length/2 - mount_hole_offset]:
    result = result - Pos(0, 0, z_pos) * Rot(0, 90, 0) * Cylinder(mount_hole_diameter/2, arm_width + 10)

part = result
part.name = "arm_with_rib_and_holes"
export_step(part, "output.step")