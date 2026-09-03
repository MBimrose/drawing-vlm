from build123d import *

arm_length = 80.0
arm_width = 30.0
arm_thickness = 10.0
rib_width = 6.0
rib_height = 4.0
rib_length = 50.0
pocket_width = 15.0
pocket_depth = 3.0
slot_width = 8.0
slot_height = 12.0
slot_offset_from_front = 5.0
hole_diameter = 5.0
hole_depth = 8.0
hole_offset_from_left = 20.0
chamfer_distance = 0.8
groove_width = 4.0
groove_depth = 5.0
groove_length = 50.0

solid_body = Box(arm_length, arm_width, arm_thickness)
solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_distance)

rib = Pos(0, 0, arm_thickness/2 + rib_height/2) * Box(rib_length, rib_width, rib_height)
solid_body = solid_body + rib

pocket = Pos(0, 0, arm_thickness/2 - pocket_depth/2) * Box(pocket_width, arm_thickness, pocket_depth)
solid_body = solid_body - pocket

slot_y = arm_width/2 - slot_offset_from_front - slot_width/2
slot = Pos(0, slot_y, 0) * Box(slot_width, slot_height, arm_thickness)
solid_body = solid_body - slot

hole_x = -arm_length/2 + hole_offset_from_left
hole = Pos(hole_x, 0, arm_thickness/2 - hole_depth/2) * Cylinder(hole_diameter/2, hole_depth)
solid_body = solid_body - hole

groove = Pos(0, -arm_width/2 + groove_depth/2, 0) * Box(groove_length, groove_depth, groove_width)
solid_body = solid_body - groove

part = solid_body
part.name = "arm_with_features"
export_step(part, "output.step")