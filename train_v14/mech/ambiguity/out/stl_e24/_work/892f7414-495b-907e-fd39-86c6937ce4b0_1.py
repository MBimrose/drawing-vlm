from build123d import *

arm_length = 80
arm_width = 30
arm_thickness = 10
rib_height = 2
rib_width = 3
rib_spacing = 4
rib_count = 5
hole_diameter = 10
chamfer_distance = 0.5
gusset_thickness = 4
gusset_height = 15
gusset_offset = 20

result = Box(arm_length, arm_width, arm_thickness)

for i in range(rib_count):
    y_pos = -arm_width/2 + rib_spacing + i * (rib_width + rib_spacing) + rib_width/2
    rib = Pos(0, y_pos, arm_thickness/2 + rib_height/2) * Box(rib_width, rib_height, rib_height)
    result = result + rib

gusset = Pos(-arm_length/2 + gusset_offset, 0, -arm_thickness/2 - gusset_height/2) * Box(gusset_thickness, gusset_height, gusset_height)
result = result + gusset

result = result - Cylinder(hole_diameter/2, 100)

top_face = result.faces().sort_by(Axis.Z)[-1]
result = chamfer(top_face.edges(), chamfer_distance)

part = result
part.name = "ribbed_arm_with_gusset"
export_step(part, "output.step")