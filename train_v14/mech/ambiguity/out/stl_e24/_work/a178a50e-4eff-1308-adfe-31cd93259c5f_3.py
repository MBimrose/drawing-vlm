from build123d import *

bracket_length = 80.0
bracket_width = 40.0
bracket_thickness = 5.0
boss_diameter = 20.0
boss_height = 10.0
hole_diameter = 4.0
hole_spacing_x = 15.0
hole_spacing_y = 12.0
hole_rows = 2
hole_columns = 4
fillet_radius = 1.5
chamfer_distance = 0.5
rib_thickness = 2.0
rib_width = 5.0
rib_offset = 8.0

base = Pos(0, 0, bracket_thickness/2) * Box(bracket_length, bracket_width, bracket_thickness)
base = fillet(base.edges().filter_by(Axis.Z), fillet_radius)
bottom_face = base.faces().sort_by(Axis.Z)[0]
base = chamfer(bottom_face.edges(), chamfer_distance)

boss = Pos(0, 0, bracket_thickness + boss_height/2) * Cylinder(boss_diameter/2, boss_height)
result = base + boss

rib = Pos(0, -bracket_width/2 + rib_offset, -rib_thickness/2) * Box(bracket_length - 10, rib_width, rib_thickness)
result = result + rib

for row in range(hole_rows):
    for col in range(hole_columns):
        x = (col - (hole_columns - 1) / 2) * hole_spacing_x
        y = (row - (hole_rows - 1) / 2) * hole_spacing_y
        hole = Pos(x, y, bracket_thickness + boss_height/2) * Cylinder(hole_diameter/2, bracket_thickness + boss_height + 20)
        result = result - hole

part = result
part.name = "bracket"
export_step(part, "output.step")