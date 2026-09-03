from build123d import *

arm_length = 70.0
arm_radius = 10.0
fillet_radius = 4.0
blind_hole_diameter = 6.0
blind_hole_depth = 12.0
rib_width = 12.0
rib_height = 3.0
rib_thickness = 2.0
slot_width = 8.0
slot_depth = 4.0
mount_hole_diameter = 4.0
mount_hole_spacing = 15.0
mount_hole_offset = 20.0

solid_body = Pos(arm_length/2, 0, 0) * Cylinder(arm_radius, arm_length)
solid_body = fillet(solid_body.edges(), fillet_radius)

slot_box = Pos(arm_length/2, 0, arm_radius - slot_depth/2) * Box(slot_width, slot_depth, slot_depth)
solid_body = solid_body - slot_box

blind_hole = Pos(arm_length/2, 0, arm_radius - blind_hole_depth/2) * Cylinder(blind_hole_diameter/2, blind_hole_depth)
solid_body = solid_body - blind_hole

rib = Pos(arm_length/2, 0, arm_radius - rib_thickness/2) * Box(rib_width, rib_height, rib_thickness)
solid_body = solid_body + rib

for i in range(2):
    x_pos = arm_length/2 + mount_hole_offset + i * mount_hole_spacing
    hole = Pos(x_pos, 0, 0) * Rot(90, 0, 0) * Cylinder(mount_hole_diameter/2, arm_radius * 2)
    solid_body = solid_body - hole

part = solid_body
part.name = "arm_with_features"
export_step(part, "output.step")