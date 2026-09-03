from build123d import *

arm_length = 80.0
arm_width = 30.0
arm_thickness = 10.0
rib_height = 15.0
rib_thickness = 4.0
rib_offset = 20.0
hole_diameter = 10.0
hole_center_x = 40.0
hole_center_y = 0.0
chamfer_size = 0.5
small_rib_height = 2.0
small_rib_width = 3.0
small_rib_spacing = 8.0
small_rib_count = 4
small_rib_offset = 25.0

base = Pos(arm_length/2, 0, arm_thickness/2) * Box(arm_length, arm_width, arm_thickness)
rib = Pos(rib_offset, 0, -rib_height/2) * Box(rib_thickness, arm_width, rib_height)
result = base + rib

for i in range(small_rib_count):
    y_pos = -arm_width/2 + small_rib_spacing/2 + i * small_rib_spacing
    small_rib = Pos(small_rib_offset, y_pos, arm_thickness + small_rib_height/2) * Box(small_rib_width, small_rib_height, small_rib_height)
    result = result + small_rib

hole = Pos(hole_center_x, hole_center_y, 0) * Cylinder(hole_diameter/2, 50)
result = result - hole

top_face = result.faces().sort_by(Axis.Z)[-1]
result = chamfer(top_face.edges(), chamfer_size)

part = result
part.name = "arm_with_ribs"
export_step(part, "output.step")