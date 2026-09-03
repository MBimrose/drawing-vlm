from build123d import *

arm_length = 80.0
arm_width = 30.0
arm_thickness = 10.0
slot_width = 12.0
slot_height = 8.0
slot_offset_from_end = 15.0
hole_diameter = 5.0
hole_offset_from_end = 20.0
rib_height = 4.0
rib_width = 6.0
rib_length = arm_length * 0.6
pocket_width = 15.0
pocket_height = 10.0
pocket_depth = 3.0
groove_width = 4.0
groove_length = arm_length * 0.6
groove_depth = 5.0
chamfer_size = 0.8

solid_body = Box(arm_length, arm_width, arm_thickness)
solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_size)

slot_center_x = -arm_length / 2 + slot_offset_from_end + slot_width / 2
slot_cut = Pos(slot_center_x, arm_width/2 - arm_thickness/2, 0) * Box(slot_width, arm_thickness, slot_height)
solid_body = solid_body - slot_cut

hole_center_x = -arm_length / 2 + hole_offset_from_end
hole_cut = Pos(hole_center_x, 0, 0) * Cylinder(hole_diameter/2, arm_thickness)
solid_body = solid_body - hole_cut

rib = Pos(0, 0, arm_thickness/2 + rib_height/2) * Box(rib_length, rib_width, rib_height)
solid_body = solid_body + rib

pocket_cut = Pos(0, 0, -arm_thickness/2 + pocket_depth/2) * Box(pocket_width, pocket_height, pocket_depth)
solid_body = solid_body - pocket_cut

groove_cut = Pos(0, -arm_width/2 + groove_depth/2, 0) * Box(groove_length, groove_depth, groove_width)
solid_body = solid_body - groove_cut

part = solid_body
part.name = "arm_with_features"
export_step(part, "output.step")