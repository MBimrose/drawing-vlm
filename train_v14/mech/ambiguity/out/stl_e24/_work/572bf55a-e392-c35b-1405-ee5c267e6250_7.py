from build123d import *

panel_width = 80.0
panel_height = 50.0
panel_thickness = 5.0
corner_fillet_radius = 4.0
boss_width = 30.0
boss_height = 20.0
boss_thickness = 3.0
hole_diameter = 7.0
hole_spacing = 8.0
hole_count = 9
hole_row_offset_y = -panel_height/4
pocket_radius = 8.0
pocket_depth = 2.5

base = Box(panel_width, panel_height, panel_thickness)
boss = Box(boss_width, boss_height, boss_thickness)
result = base + boss

result = fillet(result.edges().filter_by(Axis.Z), corner_fillet_radius)

pocket = Pos(0, 0, panel_thickness/2 - pocket_depth/2) * Cylinder(pocket_radius, pocket_depth)
result = result - pocket

start_x = -((hole_count-1)*hole_spacing)/2
for i in range(hole_count):
    x = start_x + i * hole_spacing
    hole = Pos(x, hole_row_offset_y, 0) * Cylinder(hole_diameter/2, panel_thickness + 1)
    result = result - hole

part = result
part.name = "panel_with_boss_and_holes"
export_step(part, "output.step")