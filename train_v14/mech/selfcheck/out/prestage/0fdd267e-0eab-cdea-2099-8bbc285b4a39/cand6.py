from build123d import *

arm_length = 80.0
arm_width = 15.0
arm_thickness = 8.0
flange_length = 30.0
hole_diameter = 12.0
chamfer_size = 1.0

base = Pos(arm_length/2, arm_width/2, arm_thickness/2) * Box(arm_length, arm_width, arm_thickness)
flange = Pos(arm_length + flange_length/2, arm_width/2, arm_thickness/2) * Box(flange_length, arm_width, arm_thickness)
solid_body = base + flange

hole_center_x = arm_length + flange_length/2
hole_center_y = arm_width/2
solid_body = solid_body - Pos(hole_center_x, hole_center_y, arm_thickness/2) * Cylinder(hole_diameter/2, arm_thickness * 2)

solid_body = chamfer(solid_body.edges(), chamfer_size)

part = solid_body
part.name = "arm_with_flange"
export_step(part, "output.step")