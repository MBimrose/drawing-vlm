from build123d import *

jaw_length = 80.0
jaw_width = 30.0
jaw_thickness = 10.0
rib_height = 15.0
rib_thickness = 2.0
rib_width = 4.0
rib_spacing = 6.0
rib_count = 4
hole_diameter = 10.0
chamfer_size = 0.5
pad_length = 20.0
pad_width = 30.0
pad_height = 3.0

result = Box(jaw_length, jaw_width, jaw_thickness)

rib_x = -jaw_length/2 + rib_spacing + rib_width/2
for i in range(rib_count):
    rib_y = -jaw_width/2 + rib_spacing + i * (rib_width + rib_spacing) + rib_width/2
    rib = Pos(rib_x, rib_y, -jaw_thickness/2 - rib_height/2) * Box(rib_width, rib_thickness, rib_height)
    result = result + rib

pad = Pos(0, 0, jaw_thickness/2 + pad_height/2) * Box(pad_length, pad_width, pad_height)
result = result + pad

hole = Cylinder(hole_diameter/2, jaw_thickness + pad_height + 10)
result = result - hole

top_face = result.faces().sort_by(Axis.Z)[-1]
result = chamfer(top_face.edges(), chamfer_size)

part = result
part.name = "jaw_with_ribs_and_pad"
export_step(part, "output.step")