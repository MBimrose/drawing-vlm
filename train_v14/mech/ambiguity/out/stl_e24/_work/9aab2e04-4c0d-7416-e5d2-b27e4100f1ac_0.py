from build123d import *

arm_length = 80.0
arm_width = 15.0
arm_thickness = 5.0
rib_height = 2.0
rib_width = 12.0
hole_diameter = 5.0
hole_spacing = 20.0
chamfer_size = 0.5
mount_hole_diameter = 3.0
mount_hole_offset = 2.0
pocket_depth = 2.0
pocket_margin = 5.0

base = Pos(0, 0, arm_length/2) * Box(arm_width, arm_thickness, arm_length)
rib = Pos(0, arm_thickness/2 + rib_height/2, arm_length/2) * Box(rib_width, rib_height, arm_length)
result = base + rib

result = chamfer(result.edges().filter_by(Axis.Z), chamfer_size)

for x, z in [(0, arm_length/2 - hole_spacing), (0, arm_length/2), (0, arm_length/2 + hole_spacing)]:
    result = result - Pos(x, 0, z) * Rot(90, 0, 0) * Cylinder(hole_diameter/2, arm_thickness + rib_height + 10)

for x, z in [(0, mount_hole_offset), (0, arm_length - mount_hole_offset)]:
    result = result - Pos(x, 0, z) * Rot(0, 90, 0) * Cylinder(mount_hole_diameter/2, arm_width + 10)

pocket = Pos(0, -arm_thickness/2 + pocket_depth/2, arm_length/2) * Box(arm_width - pocket_margin, pocket_depth, arm_length - 2*pocket_margin)
result = result - pocket

part = result
part.name = "arm_with_rib_and_holes"
export_step(part, "output.step")