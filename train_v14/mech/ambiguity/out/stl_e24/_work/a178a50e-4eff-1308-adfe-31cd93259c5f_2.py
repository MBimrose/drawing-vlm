from build123d import *

bracket_length = 80.0
bracket_width = 40.0
bracket_thickness = 5.0
boss_diameter = 20.0
boss_height = 10.0
hole_diameter = 4.0
hole_rows = 2
hole_cols = 4
hole_spacing_x = 15.0
hole_spacing_y = 12.0
fillet_radius = 1.5
chamfer_distance = 0.5
rib_height = 2.0
rib_width = 5.0
rib_offset = 8.0

base = Box(bracket_length, bracket_width, bracket_thickness)
boss = Pos(0, 0, bracket_thickness/2 + boss_height/2) * Cylinder(boss_diameter/2, boss_height)
result = base + boss

result = fillet(result.edges().filter_by(Axis.Z), fillet_radius)

bottom_face = result.faces().sort_by(Axis.Z)[0]
result = chamfer(bottom_face.edges(), chamfer_distance)

start_x = -((hole_cols - 1) * hole_spacing_x) / 2
start_y = -((hole_rows - 1) * hole_spacing_y) / 2
hole_points = [
    (start_x + i * hole_spacing_x, start_y + j * hole_spacing_y)
    for i in range(hole_cols)
    for j in range(hole_rows)
]

for x, y in hole_points:
    result = result - Pos(x, y, 0) * Cylinder(hole_diameter/2, 100)

rib = Pos(0, -bracket_width/2 + rib_offset, -bracket_thickness/2 - rib_height/2) * Box(bracket_length - 10, rib_width, rib_height)
result = result + rib

part = result
part.name = "bracket_with_boss_and_rib"
export_step(part, "output.step")