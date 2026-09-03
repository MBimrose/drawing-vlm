from build123d import *

lever_length = 100.0
lever_width = 15.0
lever_thickness = 8.0
tab_length = 10.0
tab_width = 12.0
hole_diameter = 12.0
groove_width = 6.0
groove_depth = 2.0
groove_length = 80.0
rib_width = 4.0
rib_height = 3.0
rib_length = 60.0
chamfer_size = 1.0

base = Box(lever_length, lever_width, lever_thickness)
tab = Pos(lever_length/2 + tab_length/2, 0, 0) * Box(tab_length, tab_width, lever_thickness)
result = base + tab
result = chamfer(result.edges(), chamfer_size)

hole_center_x = lever_length/2 + tab_length/2
result = result - Pos(hole_center_x, 0, 0) * Cylinder(hole_diameter/2, lever_thickness + 10)

groove = Pos(0, 0, lever_thickness - groove_depth/2) * Box(groove_length, groove_width, groove_depth)
result = result - groove

rib = Pos(0, 0, -rib_height/2) * Box(rib_length, rib_width, rib_height)
result = result + rib

part = result
part.name = "lever_with_tab"
export_step(part, "output.step")