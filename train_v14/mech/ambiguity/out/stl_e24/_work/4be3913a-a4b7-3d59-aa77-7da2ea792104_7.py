from build123d import *

base_width = 60.0
base_depth = 30.0
base_thickness = 8.0
boss_radius = 5.0
boss_height = 30.0
fillet_radius = 1.5
hole_diameter = 4.0
hole_spacing = 12.0
hole_rows = 5
hole_cols = 3

base = Pos(0, 0, base_thickness/2) * Box(base_width, base_depth, base_thickness)
boss = Pos(0, 0, base_thickness + boss_height/2) * Cylinder(boss_radius, boss_height)
solid_body = base + boss

vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = fillet(vertical_edges, fillet_radius)

hole_radius = hole_diameter / 2
hole_height = base_thickness + boss_height + 10
hole_center_z = (base_thickness + boss_height) / 2

for row in range(hole_rows):
    y = row * hole_spacing
    for col in range(hole_cols):
        x = (col - (hole_cols - 1) / 2) * hole_spacing
        solid_body = solid_body - Pos(x, y, hole_center_z) * Cylinder(hole_radius, hole_height)

part = solid_body
part.name = "base_with_boss_and_holes"
export_step(part, "output.step")