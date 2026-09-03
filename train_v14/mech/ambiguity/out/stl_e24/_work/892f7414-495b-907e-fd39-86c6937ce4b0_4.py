from build123d import *

arm_length = 80.0
arm_width = 30.0
arm_thickness = 10.0
rib_height = 2.0
rib_width = 2.0
rib_spacing = 4.0
rib_count = 4
hole_diameter = 10.0
chamfer_size = 0.5
web_thickness = 4.0
web_height = 15.0

base = Box(arm_length, arm_width, arm_thickness)

rib_x = -arm_length/2 + rib_spacing + rib_width/2
rib_y_positions = [(-arm_width/2 + rib_spacing + i*(rib_width + rib_spacing) + rib_width/2) for i in range(rib_count)]
rib_z = arm_thickness/2 + rib_height/2

for y in rib_y_positions:
    base = base + Pos(rib_x, y, rib_z) * Box(rib_width, rib_height, rib_height)

web_x = -arm_length/2 + web_height
web_z = -arm_thickness/2 - web_height/2
base = base + Pos(web_x, 0, web_z) * Box(web_thickness, arm_width, web_height)

base = base - Cylinder(hole_diameter/2, 100)

top_face = base.faces().sort_by(Axis.Z)[-1]
base = chamfer(top_face.edges(), chamfer_size)

part = base
part.name = "arm_with_ribs_and_web"
export_step(part, "output.step")