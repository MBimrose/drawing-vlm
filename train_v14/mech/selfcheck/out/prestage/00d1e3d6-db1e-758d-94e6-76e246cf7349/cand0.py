from build123d import *

panel_width = 80.0
panel_height = 80.0
panel_thickness = 6.0
rib_width = 4.0
rib_height = 3.0
hole_diameter = 5.0
hole_spacing = 12.0
num_holes = 5
chamfer_size = 0.5

base = Box(panel_width, panel_height, panel_thickness)
rib_left = Pos(-panel_width/2 + rib_width/2, 0, 0) * Box(rib_width, panel_height, rib_height)
rib_right = Pos(panel_width/2 - rib_width/2, 0, 0) * Box(rib_width, panel_height, rib_height)
rib_bottom = Pos(0, -panel_height/2 + rib_width/2, 0) * Box(panel_width, rib_width, rib_height)
rib_top = Pos(0, panel_height/2 - rib_width/2, 0) * Box(panel_width, rib_width, rib_height)

solid_body = base + rib_left + rib_right + rib_bottom + rib_top

for i in range(num_holes):
    x = (i - (num_holes - 1) / 2) * hole_spacing
    solid_body = solid_body - Pos(x, 0, 0) * Cylinder(hole_diameter/2, panel_thickness + 3)

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = chamfer(top_face.edges(), chamfer_size)

part = solid_body
part.name = "panel_with_ribs_and_holes"
export_step(part, "output.step")