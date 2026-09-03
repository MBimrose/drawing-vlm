from build123d import *

panel_width = 80.0
panel_height = 60.0
panel_thickness = 5.0
rib_width = 5.0
rib_height = panel_height
rib_thickness = 3.0
groove_width = 20.0
groove_depth = 2.0
groove_offset_y = panel_height/2 - 10.0
chamfer_size = 1.0
hole_diameter = 4.0
hole_offset_x = 0.0
hole_offset_y = 0.0
notch_width = 10.0
notch_height = 5.0
notch_offset_y = panel_height/2 - 5.0

base = Box(panel_width, panel_height, panel_thickness)

notch = Pos(0, notch_offset_y, panel_thickness/2) * Box(notch_width, notch_height, panel_thickness)
base = base - notch

groove = Pos(0, groove_offset_y, panel_thickness/2) * Box(groove_width, groove_depth, panel_thickness)
base = base - groove

left_rib = Pos(-panel_width/2 + rib_width/2, 0, 0) * Box(rib_width, rib_height, rib_thickness)
right_rib = Pos(panel_width/2 - rib_width/2, 0, 0) * Box(rib_width, rib_height, rib_thickness)

result = base + left_rib + right_rib

bottom_face = result.faces().sort_by(Axis.Y)[0]
result = chamfer(bottom_face.edges(), chamfer_size)

result = result - Pos(hole_offset_x, hole_offset_y, 0) * Cylinder(hole_diameter/2, panel_thickness * 2)

part = result
part.name = "panel_with_ribs"
export_step(part, "output.step")