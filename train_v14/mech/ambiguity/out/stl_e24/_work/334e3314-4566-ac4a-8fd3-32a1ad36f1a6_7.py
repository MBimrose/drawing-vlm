from build123d import *

panel_width = 80
panel_height = 50
panel_thickness = 4
tab_width = 12
tab_height = 20
boss_diameter = 20
boss_height = 6
hole_diameter = 5.2
hole_spacing = 12
num_holes = 5
chamfer_size = 0.5

base = Box(panel_width, panel_height, panel_thickness)
tab = Pos(panel_width/2 + tab_width/2, 0, 0) * Box(tab_width, tab_height, panel_thickness)
boss = Pos(0, 0, panel_thickness/2 + boss_height/2) * Cylinder(boss_diameter/2, boss_height)

solid_body = base + tab + boss

for i in range(num_holes):
    x = (i - (num_holes-1)/2) * hole_spacing
    solid_body = solid_body - Pos(x, 0, 0) * Cylinder(hole_diameter/2, 20)

solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_size)

part = solid_body
part.name = "panel_with_tab_boss_and_holes"
export_step(part, "output.step")