from build123d import *

panel_width = 80.0
panel_height = 80.0
panel_thickness = 6.0
rib_width = 12.0
rib_height = 6.0
hole_diameter = 5.0
hole_depth = 4.5
hole_spacing = 12.0
num_holes = 5
chamfer_size = 0.5

base = Box(panel_width, panel_height, panel_thickness)
rib = Pos(0, -panel_height/2 + rib_height/2, 0) * Box(rib_width, rib_height, panel_thickness)
solid_body = base + rib

hole_start_x = -((num_holes - 1) * hole_spacing) / 2
for i in range(num_holes):
    x = hole_start_x + i * hole_spacing
    solid_body = solid_body - Pos(x, 0, panel_thickness/2 - hole_depth/2) * Cylinder(hole_diameter/2, hole_depth)

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = chamfer(top_face.edges(), chamfer_size)

part = solid_body
part.name = "panel_with_rib_and_holes"
export_step(part, "output.step")