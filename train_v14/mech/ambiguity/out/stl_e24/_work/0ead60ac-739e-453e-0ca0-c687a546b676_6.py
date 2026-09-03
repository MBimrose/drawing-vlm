from build123d import *

arm_length = 80.0
arm_width = 20.0
arm_thickness = 10.0
rib_height = 6.0
rib_width = 8.0
rib_offset = 30.0
hole_diameter = 4.0
hole_spacing = 30.0
chamfer_size = 0.5

base = Box(arm_length, arm_width, arm_thickness)
rib = Pos(rib_offset, 0, 0) * Box(rib_width, rib_height, arm_thickness)
solid_body = base + rib

for x, y in [(-hole_spacing/2, 0), (hole_spacing/2, 0)]:
    solid_body = solid_body - Pos(x, y, 0) * Cylinder(hole_diameter/2, arm_thickness * 2)

solid_body = chamfer(solid_body.edges().filter_by(Axis.X), chamfer_size)

part = solid_body
part.name = "arm_with_rib"
export_step(part, "output.step")