from build123d import *

arm_length = 80.0
arm_width = 20.0
arm_thickness = 10.0
pocket_length = 40.0
pocket_width = 12.0
pocket_depth = 6.0
hole_diameter = 4.0
hole_spacing = 30.0
chamfer_size = 0.5
rib_height = 3.0
rib_thickness = 2.0
rib_spacing = 15.0

solid_body = Box(arm_length, arm_width, arm_thickness)
solid_body = chamfer(solid_body.edges().filter_by(Axis.X), chamfer_size)

pocket = Pos(0, 0, arm_thickness - pocket_depth/2) * Box(pocket_length, pocket_width, pocket_depth)
solid_body = solid_body - pocket

for x, y in [(-hole_spacing/2, 0), (hole_spacing/2, 0)]:
    solid_body = solid_body - Pos(x, y, 0) * Cylinder(hole_diameter/2, arm_thickness * 2)

num_ribs = int((arm_length - rib_spacing) // rib_spacing)
for i in range(num_ribs):
    x_pos = -arm_length/2 + rib_spacing/2 + i * rib_spacing
    rib = Pos(x_pos, 0, -arm_thickness/2 + rib_height/2) * Box(rib_thickness, arm_width, rib_height)
    solid_body = solid_body + rib

part = solid_body
part.name = "arm_with_pocket_holes_and_ribs"
export_step(part, "output.step")