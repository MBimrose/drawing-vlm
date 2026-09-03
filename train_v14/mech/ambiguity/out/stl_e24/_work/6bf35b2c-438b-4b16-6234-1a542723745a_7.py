from build123d import *

bracket_length = 80.0
bracket_width = 40.0
bracket_thickness = 8.0
rib_width = 5.0
rib_height = 12.0
rib_spacing = 15.0
rib_margin = 10.0
rib_thickness = 1.5
hole_diameter = 5.0
hole_depth = 6.0
hole_spacing_x = 20.0
hole_spacing_y = 12.0
hole_rows = 2
hole_cols = 3
fillet_radius = 2.0

solid = Box(bracket_length, bracket_width, bracket_thickness)

rib_count = int((bracket_length - 2 * rib_margin) / rib_spacing) + 1
rib_positions = [(-bracket_length/2 + rib_margin + i * rib_spacing, 0) for i in range(rib_count)]

for x, y in rib_positions:
    solid = solid + Pos(x, y, bracket_thickness/2 + rib_thickness/2) * Box(rib_width, rib_height, rib_thickness)

hole_start_x = -((hole_cols - 1) * hole_spacing_x) / 2
hole_start_y = -((hole_rows - 1) * hole_spacing_y) / 2
hole_points = [(hole_start_x + i * hole_spacing_x, hole_start_y + j * hole_spacing_y) for i in range(hole_cols) for j in range(hole_rows)]

for x, y in hole_points:
    solid = solid - Pos(x, y, -bracket_thickness/2 + hole_depth/2) * Cylinder(hole_diameter/2, hole_depth)

solid = fillet(solid.edges().filter_by(Axis.Z), fillet_radius)

part = solid
part.name = "bracket_with_ribs_and_holes"
export_step(part, "output.step")