from build123d import *

panel_width = 80.0
panel_height = 50.0
panel_thickness = 5.0
hole_diameter = 7.0
hole_spacing = 8.0
hole_row_y = -panel_height/4
fillet_radius = 4.0
rib_width = 10.0
rib_thickness = 3.0
central_pocket_radius = 8.0
central_pocket_depth = 2.5

solid_body = Box(panel_width, panel_height, panel_thickness)
solid_body = fillet(solid_body.edges().filter_by(Axis.Z), fillet_radius)

rib1 = Pos(-panel_width/2 + rib_width/2, 0, 0) * Box(rib_width, panel_height, rib_thickness)
rib2 = Pos(panel_width/2 - rib_width/2, 0, 0) * Box(rib_width, panel_height, rib_thickness)
solid_body = solid_body + rib1 + rib2

pocket = Pos(0, 0, panel_thickness/2 - central_pocket_depth/2) * Cylinder(central_pocket_radius, central_pocket_depth)
solid_body = solid_body - pocket

for i in range(9):
    x = (i - 4) * hole_spacing
    hole = Pos(x, hole_row_y, 0) * Cylinder(hole_diameter/2, panel_thickness + 10)
    solid_body = solid_body - hole

part = solid_body
part.name = "panel_with_ribs_pocket_and_holes"
export_step(part, "output.step")