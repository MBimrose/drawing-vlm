from build123d import *

arm_length = 80.0
arm_width = 30.0
arm_thickness = 10.0
slot_width = 6.0
slot_length = arm_length * 0.6
hole_diameter = 8.0
hole_offset_from_end = 10.0
chamfer_distance = 1.0
rib_height = 4.0
rib_thickness = 4.0
rib_spacing = 12.0
fillet_radius = 0.8
mount_hole_diameter = 4.0
mount_hole_spacing = 25.0

result = Box(arm_length, arm_width, arm_thickness)

slot = Box(slot_length, slot_width, arm_thickness)
result = result - slot

hole_center_x = arm_length / 2 - hole_offset_from_end
hole = Pos(hole_center_x, 0, 0) * Cylinder(hole_diameter / 2, arm_thickness)
result = result - hole

left_face = result.faces().sort_by(Axis.X)[0]
left_edges = left_face.edges()
result = chamfer(left_edges, chamfer_distance)

for x in [-mount_hole_spacing / 2, mount_hole_spacing / 2]:
    mount_hole = Pos(x, 0, 0) * Rot(90, 0, 0) * Cylinder(mount_hole_diameter / 2, arm_width)
    result = result - mount_hole

rib_length = arm_length * 0.6
for y in [-rib_spacing / 2, rib_spacing / 2]:
    rib = Pos(0, y, arm_thickness / 2 + rib_height / 2) * Box(rib_length, rib_thickness, rib_height)
    result = result + rib

vertical_edges = result.edges().filter_by(Axis.Z)
result = fillet(vertical_edges, fillet_radius)

part = result
part.name = "arm_with_slot_and_ribs"
export_step(part, "output.step")