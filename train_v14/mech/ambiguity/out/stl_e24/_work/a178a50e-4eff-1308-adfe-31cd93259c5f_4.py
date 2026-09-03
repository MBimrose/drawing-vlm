from build123d import *

bracket_length = 80
bracket_width = 40
bracket_thickness = 5
boss_diameter = 20
boss_height = 10
hole_diameter = 4
hole_spacing_x = 15
hole_spacing_y = 12
hole_rows = 2
hole_cols = 4
fillet_radius = 1.5
chamfer_distance = 0.5
rib_height = 2
rib_thickness = 4
rib_offset = 5

base = Pos(0, 0, bracket_thickness/2) * Box(bracket_length, bracket_width, bracket_thickness)
boss = Pos(0, 0, bracket_thickness + boss_height/2) * Cylinder(boss_diameter/2, boss_height)
result = base + boss

result = fillet(result.edges().filter_by(Axis.Z), fillet_radius)

bottom_face = result.faces().sort_by(Axis.Z)[0]
result = chamfer(bottom_face.edges(), chamfer_distance)

for i in range(hole_cols):
    for j in range(hole_rows):
        x = (i - (hole_cols-1)/2) * hole_spacing_x
        y = (j - (hole_rows-1)/2) * hole_spacing_y
        result = result - Pos(x, y, bracket_thickness/2 + boss_height/2) * Cylinder(hole_diameter/2, bracket_thickness + boss_height + 10)

rib = Pos(0, -bracket_width/2 + rib_offset + rib_thickness/2, -rib_height/2) * Box(bracket_length - 2*rib_offset, rib_thickness, rib_height)
result = result + rib

part = result
part.name = "bracket"
export_step(part, "output.step")