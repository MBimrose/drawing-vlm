from build123d import *

arm_length = 80.0
arm_width = 30.0
arm_thickness = 6.0
slot_width = 4.0
slot_length = 20.0
slot_depth = 3.0
boss_diameter = 12.0
boss_height = 4.0
fillet_radius = 1.0
chamfer_distance = 0.7
mount_hole_diameter = 4.0
mount_hole_spacing = 40.0

solid_body = Box(arm_width, arm_thickness, arm_length)

solid_body = fillet(solid_body.edges().filter_by(Axis.Z), fillet_radius)

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = chamfer(top_face.edges(), chamfer_distance)

slot_box = Pos(arm_width/2 - slot_depth/2, 0, -arm_length/2 + slot_length/2) * Box(slot_depth, slot_width, slot_length)
solid_body = solid_body - slot_box

boss_cyl = Pos(0, arm_thickness/2, -arm_length/2) * Rot(90, 0, 0) * Cylinder(boss_diameter/2, boss_height)
solid_body = solid_body + boss_cyl

for x, y in [(-mount_hole_spacing/2, 0), (mount_hole_spacing/2, 0)]:
    hole = Pos(x, y, 0) * Cylinder(mount_hole_diameter/2, arm_length + 10)
    solid_body = solid_body - hole

part = solid_body
part.name = "arm_with_slot_boss_and_mount_holes"
export_step(part, "output.step")