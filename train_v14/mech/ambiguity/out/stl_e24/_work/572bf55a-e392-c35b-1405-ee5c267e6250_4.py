from build123d import *

panel_width = 80.0
panel_height = 50.0
panel_thickness = 5.0
corner_fillet_radius = 4.0
hole_diameter = 7.0
hole_spacing = 8.0
hole_count = 9
hole_row_y = -panel_height / 4.0
boss_radius = 8.0
boss_depth = 2.5

solid_body = Box(panel_width, panel_height, panel_thickness)
solid_body = fillet(solid_body.edges().filter_by(Axis.Z), corner_fillet_radius)

for i in range(hole_count):
    x = -((hole_count - 1) * hole_spacing) / 2.0 + i * hole_spacing
    solid_body = solid_body - Pos(x, hole_row_y, 0) * Cylinder(hole_diameter / 2, panel_thickness)

solid_body = solid_body - Pos(0, 0, panel_thickness / 2 - boss_depth / 2) * Cylinder(boss_radius, boss_depth)

part = solid_body
part.name = "panel_with_holes_and_boss"
export_step(part, "output.step")