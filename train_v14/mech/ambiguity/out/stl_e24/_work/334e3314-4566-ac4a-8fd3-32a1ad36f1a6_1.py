from build123d import *

panel_width = 80.0
panel_depth = 50.0
panel_thickness = 4.0
tab_width = 10.0
tab_height = 20.0
boss_diameter = 20.0
boss_height = 6.0
hole_diameter = 5.2
hole_spacing = 12.0
hole_count = 5
chamfer_size = 0.5

base = Box(panel_width, panel_depth, panel_thickness)
tab = Pos(panel_width/2 + tab_width/2, 0, 0) * Box(tab_width, tab_height, panel_thickness)
result = base + tab

boss = Pos(0, 0, panel_thickness/2 + boss_height/2) * Cylinder(boss_diameter/2, boss_height)
result = result + boss

for i in range(hole_count):
    x = (i - (hole_count - 1) / 2) * hole_spacing
    result = result - Pos(x, 0, 0) * Cylinder(hole_diameter/2, 20)

result = chamfer(result.edges().filter_by(Axis.Z), chamfer_size)

part = result
part.name = "panel_with_tabs_boss_and_holes"
export_step(part, "output.step")