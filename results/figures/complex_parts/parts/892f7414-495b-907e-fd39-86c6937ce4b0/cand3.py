from build123d import *

arm_length = 80.0
arm_width = 30.0
arm_thickness = 10.0
hole_diameter = 10.0
rib_width = 3.0
rib_height = 2.0
rib_spacing = 5.0
rib_offset = 5.0
chamfer_size = 0.5

rib_count = int((arm_width - 2 * rib_offset) / rib_spacing) + 1

solid_body = Box(arm_length, arm_width, arm_thickness)
solid_body = solid_body - Cylinder(hole_diameter / 2, arm_thickness)

for i in range(rib_count):
    y_pos = (i - (rib_count - 1) / 2) * rib_spacing
    rib = Pos(-arm_length / 2 + rib_offset + rib_width / 2, y_pos, arm_thickness / 2 + rib_height / 2) * Box(rib_width, rib_height, arm_thickness)
    solid_body = solid_body + rib

for i in range(rib_count):
    y_pos = (i - (rib_count - 1) / 2) * rib_spacing
    rib = Pos(-arm_length / 2 + rib_offset + rib_width / 2, y_pos, -arm_thickness / 2 - rib_height / 2) * Box(rib_width, rib_height, arm_thickness)
    solid_body = solid_body + rib

vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = chamfer(vertical_edges, chamfer_size)

part = solid_body
part.name = "ribbed_plate"
export_step(part, "output.step")