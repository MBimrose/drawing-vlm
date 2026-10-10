from build123d import *

arm_length = 80.0
arm_width = 30.0
arm_thickness = 10.0
hole_diameter = 10.0
rib_height = 3.0
rib_width = 2.0
rib_spacing = 6.0
rib_margin = 5.0
chamfer_size = 0.5
tab_length = 15.0
tab_width = 5.0
tab_thickness = 3.0

result = Box(arm_length, arm_width, arm_thickness)
result = result - Cylinder(hole_diameter/2, arm_thickness)

rib_count = int((arm_width - 2 * rib_margin) / rib_spacing) + 1
for i in range(rib_count):
    y_pos = -arm_width/2 + rib_margin + i * rib_spacing
    rib = Pos(-arm_length/4, y_pos, arm_thickness/2 + rib_height/2) * Box(rib_width, rib_height, rib_height)
    result = result + rib

tab = Pos(-arm_length/2 + tab_length/2, 0, -arm_thickness/2 - tab_length/2) * Box(tab_width, tab_thickness, tab_length)
result = result + tab

top_face = result.faces().sort_by(Axis.Z)[-1]
top_edges = top_face.edges()
result = chamfer(top_edges, chamfer_size)

part = result
part.name = "arm_with_ribs_and_tab"
export_step(part, "output.step")