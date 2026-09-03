from build123d import *

arm_length = 80.0
arm_width = 30.0
arm_thickness = 10.0
pivot_hole_diameter = 8.0
pivot_hole_offset = 10.0
rib_height = 4.0
rib_width = 4.0
rib_length = arm_length * 0.6
rib_spacing = arm_width / 3.0
chamfer_distance = 1.0
fillet_radius = 0.8
mount_hole_diameter = 4.0
mount_hole_spacing = 25.0
mount_hole_offset = 12.0

solid_body = Box(arm_length, arm_width, arm_thickness)

solid_body = solid_body - Pos(arm_length/2 - pivot_hole_offset, 0, 0) * Cylinder(pivot_hole_diameter/2, arm_thickness)

for x in [-mount_hole_spacing/2, mount_hole_spacing/2]:
    solid_body = solid_body - Pos(x, 0, 0) * Rot(90, 0, 0) * Cylinder(mount_hole_diameter/2, arm_width)

for y in [-rib_spacing, 0, rib_spacing]:
    solid_body = solid_body + Pos(0, y, arm_thickness/2 + rib_height/2) * Box(rib_length, rib_width, rib_height)

left_face = solid_body.faces().sort_by(Axis.X)[0]
solid_body = chamfer(left_face.edges(), chamfer_distance)

vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = fillet(vertical_edges, fillet_radius)

part = solid_body
part.name = "arm_with_ribs"
export_step(part, "output.step")