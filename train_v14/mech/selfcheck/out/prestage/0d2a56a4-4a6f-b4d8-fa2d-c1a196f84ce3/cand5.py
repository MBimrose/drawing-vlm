from build123d import *

arm_length = 80.0
arm_width = 30.0
arm_thickness = 10.0
pivot_hole_diameter = 8.0
pivot_hole_offset = 10.0
mount_hole_diameter = 4.0
mount_hole_spacing = 25.0
rib_height = 4.0
rib_width = 4.0
rib_length = 50.0
rib_spacing = 14.0
chamfer_distance = 1.0
fillet_radius = 0.8

result = Box(arm_length, arm_width, arm_thickness)

pivot_x = arm_length / 2 - pivot_hole_offset
result = result - Pos(pivot_x, 0, 0) * Cylinder(pivot_hole_diameter / 2, arm_thickness * 2)

mount_y = arm_width / 2
for x in [-mount_hole_spacing / 2, mount_hole_spacing / 2]:
    result = result - Pos(x, 0, 0) * Rot(90, 0, 0) * Cylinder(mount_hole_diameter / 2, arm_width * 2)

rib1 = Pos(0, -rib_spacing / 2, arm_thickness / 2 + rib_height / 2) * Box(rib_length, rib_width, rib_height)
rib2 = Pos(0, rib_spacing / 2, arm_thickness / 2 + rib_height / 2) * Box(rib_length, rib_width, rib_height)
result = result + rib1 + rib2

left_face = result.faces().sort_by(Axis.X)[0]
result = chamfer(left_face.edges(), chamfer_distance)

result = fillet(result.edges().filter_by(Axis.Z), fillet_radius)

part = result
part.name = "arm_with_ribs"
export_step(part, "output.step")