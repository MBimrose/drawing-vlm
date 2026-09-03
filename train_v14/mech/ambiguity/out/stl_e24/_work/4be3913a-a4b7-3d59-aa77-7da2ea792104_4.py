from build123d import *

plate_width = 60.0
plate_depth = 30.0
plate_thickness = 8.0
boss_radius = 5.0
boss_height = 30.0
hole_diameter = 4.0
hole_spacing_x = 12.0
hole_spacing_y = 12.0
hole_rows = 2
hole_cols = 3
fillet_radius = 1.5
hole_offset_x = - (hole_cols - 1) * hole_spacing_x / 2
hole_offset_y = - (hole_rows - 1) * hole_spacing_y / 2

base = Pos(0, 0, plate_thickness / 2) * Box(plate_width, plate_depth, plate_thickness)
boss = Pos(0, 0, plate_thickness + boss_height / 2) * Cylinder(boss_radius, boss_height)
solid_body = base + boss

for i in range(hole_cols):
    for j in range(hole_rows):
        x = hole_offset_x + i * hole_spacing_x
        y = hole_offset_y + j * hole_spacing_y
        solid_body = solid_body - Pos(x, y, plate_thickness / 2) * Cylinder(hole_diameter / 2, plate_thickness + 10)

vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = fillet(vertical_edges, fillet_radius)

part = solid_body
part.name = "plate_with_boss_and_holes"
export_step(part, "output.step")