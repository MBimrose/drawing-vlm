from build123d import *

arm_length = 80
arm_width = 30
arm_thickness = 10
rib_length = 50
rib_width = 6
rib_height = 4
pocket_width = 15
pocket_length = 10
pocket_depth = 3
slot_width = 8
slot_height = 8
slot_depth = 12
hole_diameter = 5
hole_offset_from_end = 20
chamfer_size = 0.8
groove_width = 4
groove_depth = 5
groove_length = 50

solid_body = Box(arm_length, arm_width, arm_thickness)
solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_size)

solid_body = solid_body + Pos(0, 0, arm_thickness/2 + rib_height/2) * Box(rib_length, rib_width, rib_height)
solid_body = solid_body - Pos(0, 0, arm_thickness/2 - pocket_depth/2) * Box(pocket_width, pocket_length, pocket_depth)
solid_body = solid_body - Pos(0, arm_width/2 - slot_depth/2, 0) * Box(slot_width, slot_depth, slot_height)
solid_body = solid_body - Pos(-arm_length/2 + hole_offset_from_end, 0, 0) * Cylinder(hole_diameter/2, arm_thickness)
solid_body = solid_body - Pos(0, -arm_width/2 + groove_depth/2, 0) * Box(groove_length, groove_depth, groove_width)

part = solid_body
part.name = "arm_with_features"
export_step(part, "output.step")