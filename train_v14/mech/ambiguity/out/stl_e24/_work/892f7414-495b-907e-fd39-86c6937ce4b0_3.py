from build123d import *

jaw_length = 80.0
jaw_width = 30.0
jaw_thickness = 10.0
rib_height = 20.0
rib_thickness = 4.0
rib_offset = 15.0
hole_diameter = 10.0
chamfer_size = 0.8
top_rib_height = 2.0
top_rib_width = 2.0
top_rib_spacing = 6.0
top_rib_count = 4

result = Box(jaw_length, jaw_width, jaw_thickness)

rib_x = -jaw_length/2 + rib_offset + rib_thickness/2
rib_z = -jaw_thickness/2 - rib_height/2
result = result + Pos(rib_x, 0, rib_z) * Box(rib_thickness, jaw_width, rib_height)

for i in range(top_rib_count):
    y_pos = -jaw_width/2 + top_rib_spacing + i * top_rib_spacing
    z_pos = jaw_thickness/2 + top_rib_height/2
    result = result + Pos(0, y_pos, z_pos) * Box(top_rib_width, top_rib_width, top_rib_height)

result = result - Cylinder(hole_diameter/2, jaw_thickness + 2)

result = chamfer(result.edges().filter_by(Axis.Z), chamfer_size)

part = result
part.name = "jaw_with_ribs"
export_step(part, "output.step")