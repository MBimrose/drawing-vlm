from build123d import *

panel_width = 80.0
panel_height = 50.0
panel_thickness = 4.0
tab_width = 12.0
tab_height = 20.0
boss_diameter = 20.0
boss_height = 6.0
hole_diameter = 5.2
hole_spacing = 12.0
hole_count = 5
chamfer_size = 0.5

base = Box(panel_width, panel_height, panel_thickness)
tab = Pos(panel_width/2 + tab_width/2, 0, 0) * Box(tab_width, tab_height, panel_thickness)
boss = Pos(0, 0, panel_thickness/2 + boss_height/2) * Cylinder(boss_diameter/2, boss_height)

solid_body = base + tab + boss

hole_start_x = -((hole_count - 1) * hole_spacing) / 2
hole_positions = [(hole_start_x + i * hole_spacing, 0) for i in range(hole_count)]
for x, y in hole_positions:
    solid_body = solid_body - Pos(x, y, 0) * Cylinder(hole_diameter/2, 20)

solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_size)

part = solid_body
part.name = "panel_with_tab_boss_and_holes"
export_step(part, "output.step")