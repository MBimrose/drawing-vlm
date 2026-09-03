from build123d import *

jaw_length = 80.0
jaw_width = 30.0
jaw_thickness = 10.0
slot_width = 6.0
slot_length = jaw_length * 0.6
hole_diameter = 8.0
hole_offset_from_end = 10.0
chamfer_distance = 1.0
fillet_radius = 0.8
rib_height = 4.0
rib_width = 4.0
rib_spacing = 10.0
mount_hole_dia = 4.0
mount_hole_offset = 12.0

result = Box(jaw_length, jaw_width, jaw_thickness)

slot = Box(slot_length, slot_width, jaw_thickness)
result = result - slot

hole_center_x = jaw_length / 2 - hole_offset_from_end
hole = Pos(hole_center_x, 0, 0) * Cylinder(hole_diameter / 2, jaw_thickness)
result = result - hole

left_face = result.faces().sort_by(Axis.X)[0]
result = chamfer(left_face.edges(), chamfer_distance)

rib_length = jaw_length * 0.6
rib1 = Pos(0, -rib_spacing / 2, jaw_thickness / 2 + rib_height / 2) * Box(rib_length, rib_width, rib_height)
rib2 = Pos(0, rib_spacing / 2, jaw_thickness / 2 + rib_height / 2) * Box(rib_length, rib_width, rib_height)
result = result + rib1 + rib2

for x in [-jaw_length / 2 + mount_hole_offset, -jaw_length / 2 + mount_hole_offset + 25]:
    mount_hole = Pos(x, 0, 0) * Rot(90, 0, 0) * Cylinder(mount_hole_dia / 2, jaw_width)
    result = result - mount_hole

result = fillet(result.edges().filter_by(Axis.Z), fillet_radius)

part = result
part.name = "jaw_with_ribs_and_holes"
export_step(part, "output.step")