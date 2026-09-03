from build123d import *

panel_width = 80
panel_height = 50
panel_thickness = 5
hole_diameter = 11
hole_spacing = 12
hole_count = 6
fillet_radius = 3
rib_width = 10
rib_height = 5
pocket_width = 20
pocket_height = 10
pocket_offset_x = -panel_width/2 + pocket_width/2 + 5

solid_body = Box(panel_width, panel_height, panel_thickness)
solid_body = fillet(solid_body.edges().filter_by(Axis.Z), fillet_radius)

rib = Pos(0, panel_height/2 - rib_height/2, 0) * Box(rib_width, rib_height, panel_thickness)
solid_body = solid_body + rib

pocket = Pos(pocket_offset_x, 0, panel_thickness/4) * Box(pocket_width, pocket_height, panel_thickness/2)
solid_body = solid_body - pocket

for i in range(hole_count):
    x = (i - (hole_count - 1) / 2) * hole_spacing
    solid_body = solid_body - Pos(x, 0, 0) * Cylinder(hole_diameter/2, panel_thickness)

part = solid_body
part.name = "panel_with_rib_pocket_holes"
export_step(part, "output.step")