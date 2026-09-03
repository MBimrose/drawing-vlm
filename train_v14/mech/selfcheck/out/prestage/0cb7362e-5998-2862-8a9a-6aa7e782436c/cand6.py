from build123d import *

arm_length = 80.0
arm_width = 30.0
arm_thickness = 10.0
rib_width = 12.0
rib_height = 6.0
rib_offset = 5.0
hole_diameter = 4.0
counterbore_diameter = 7.0
counterbore_depth = 2.0
chamfer_size = 1.0

base = Pos(0, 0, arm_thickness/2) * Box(arm_length, arm_width, arm_thickness)
rib = Pos(0, arm_width/2 - rib_offset - rib_width/2, arm_thickness/2) * Box(rib_width, rib_height, arm_thickness)
solid_body = base + rib

hole_x = arm_length/2 - chamfer_size - 2
solid_body = solid_body - Pos(hole_x, 0, arm_thickness/2) * Cylinder(hole_diameter/2, arm_thickness + 2)
solid_body = solid_body - Pos(hole_x, 0, counterbore_depth/2) * Cylinder(counterbore_diameter/2, counterbore_depth)

vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = chamfer(vertical_edges, chamfer_size)

part = solid_body
part.name = "arm_with_rib_and_counterbore"
export_step(part, "output.step")