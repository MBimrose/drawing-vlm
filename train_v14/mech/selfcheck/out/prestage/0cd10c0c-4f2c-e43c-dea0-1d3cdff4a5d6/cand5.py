from build123d import *

arm_length = 80.0
arm_width = 20.0
arm_thickness = 10.0
tab_length = 30.0
tab_width = 10.0
pocket_length = 20.0
pocket_width = 10.0
pocket_depth = 4.0
hole_diameter = 4.0
hole_spacing = 12.0
hole_count = 6
hole_offset_from_end = 15.0
chamfer_distance = 1.0

base = Box(arm_length, arm_width, arm_thickness)
tab = Pos(arm_length/2 + tab_length/2, 0, 0) * Box(tab_length, tab_width, arm_thickness)
solid_body = base + tab

pocket = Pos(0, 0, arm_thickness/2 - pocket_depth/2) * Box(pocket_length, pocket_width, pocket_depth)
solid_body = solid_body - pocket

for i in range(hole_count):
    x = -arm_length/2 + hole_offset_from_end + i * hole_spacing
    solid_body = solid_body - Pos(x, 0, 0) * Cylinder(hole_diameter/2, arm_thickness * 2)

solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_distance)

part = solid_body
part.name = "arm_with_tab_pocket_and_holes"
export_step(part, "output.step")