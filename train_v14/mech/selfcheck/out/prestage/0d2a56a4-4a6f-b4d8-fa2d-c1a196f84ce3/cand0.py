from build123d import *

arm_length = 80.0
arm_width = 30.0
arm_thickness = 10.0
pivot_hole_diameter = 8.0
pivot_hole_offset = 10.0
mount_hole_diameter = 4.0
mount_hole_spacing = 25.0
mount_hole_offset = 12.0
rib_height = 4.0
rib_width = 4.0
rib_spacing = 10.0
chamfer_distance = 1.0
fillet_radius = 0.8

solid_body = Box(arm_length, arm_width, arm_thickness)

pivot_x = arm_length / 2 - pivot_hole_offset
solid_body = solid_body - Pos(pivot_x, 0, 0) * Cylinder(pivot_hole_diameter / 2, arm_thickness * 2)

mount_x = -arm_length / 2 + mount_hole_offset
for i in range(2):
    x = mount_x + (i - 0.5) * mount_hole_spacing
    solid_body = solid_body - Pos(x, 0, 0) * Rot(90, 0, 0) * Cylinder(mount_hole_diameter / 2, arm_width * 2)

rib_length = arm_length - 2 * pivot_hole_offset
for i in range(2):
    y = (i - 0.5) * rib_spacing
    rib = Pos(0, y, arm_thickness / 2 + rib_height / 2) * Box(rib_length, rib_width, rib_height)
    solid_body = solid_body + rib

left_face = solid_body.faces().sort_by(Axis.X)[0]
solid_body = chamfer(left_face.edges(), chamfer_distance)

solid_body = fillet(solid_body.edges().filter_by(Axis.Z), fillet_radius)

part = solid_body
part.name = "arm_with_ribs"
export_step(part, "output.step")