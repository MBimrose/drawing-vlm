from build123d import *

panel_width = 80
panel_height = 50
panel_thickness = 5
hole_diameter = 11
hole_spacing = 12
hole_count = 5
hole_start_x = -panel_width/2 + 20
fillet_radius = 3
rib_width = 10
rib_height = panel_height * 0.6
pocket_width = 20
pocket_height = 10
pocket_depth = panel_thickness / 2

base = Box(panel_width, panel_height, panel_thickness)
base = fillet(base.edges().filter_by(Axis.Z), fillet_radius)

rib = Pos(-panel_width/2 + rib_width/2, 0, 0) * Box(rib_width, rib_height, panel_thickness)
base = base + rib

pocket = Pos(-panel_width/2 + pocket_width/2 + 5, 0, panel_thickness/2 - pocket_depth/2) * Box(pocket_width, pocket_height, pocket_depth)
base = base - pocket

for i in range(hole_count):
    x = hole_start_x + i * hole_spacing
    base = base - Pos(x, 0, 0) * Cylinder(hole_diameter/2, panel_thickness * 2)

part = base
part.name = "panel_with_rib_pocket_holes"
export_step(part, "output.step")