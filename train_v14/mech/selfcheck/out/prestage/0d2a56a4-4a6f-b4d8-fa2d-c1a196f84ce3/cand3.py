from build123d import *

arm_length = 80.0
arm_width = 30.0
arm_thickness = 10.0
slot_width = 6.0
slot_length = arm_length * 0.6
hole_diameter = 8.0
hole_offset_from_end = 10.0
chamfer_distance = 1.0
fillet_radius = 0.8
rib_height = 4.0
rib_width = 4.0
rib_spacing = 10.0
mount_hole_diameter = 4.0
mount_hole_offset = 12.0

result = Box(arm_length, arm_width, arm_thickness)
result = result - Box(slot_length, slot_width, arm_thickness)

hole_center_x = arm_length / 2 - hole_offset_from_end
result = result - Pos(hole_center_x, 0, 0) * Cylinder(hole_diameter / 2, arm_thickness)

rib_length = arm_length * 0.6
rib_y_positions = [-(arm_width / 2 - rib_spacing - rib_width / 2),
                   (arm_width / 2 - rib_spacing - rib_width / 2)]
for y in rib_y_positions:
    result = result + Pos(0, y, arm_thickness / 2 + rib_height / 2) * Box(rib_length, rib_width, rib_height)

mount_x_positions = [-arm_length / 2 + mount_hole_offset,
                     -arm_length / 2 + mount_hole_offset + 25]
for x in mount_x_positions:
    result = result - Pos(x, 0, 0) * Rot(90, 0, 0) * Cylinder(mount_hole_diameter / 2, arm_width)

left_face = result.faces().sort_by(Axis.X)[0]
result = chamfer(left_face.edges(), chamfer_distance)
result = fillet(result.edges().filter_by(Axis.Z), fillet_radius)

part = result
part.name = "arm_with_ribs_and_holes"
export_step(part, "output.step")