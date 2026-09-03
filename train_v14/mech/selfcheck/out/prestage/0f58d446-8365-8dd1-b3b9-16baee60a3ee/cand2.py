from build123d import *

bracket_length = 70.0
bracket_width = 40.0
bracket_thickness = 8.0
boss_diameter = 20.0
boss_height = 12.0
boss_offset_x = -bracket_length/2 + 15.0
hole_diameter = 6.0
hole_spacing = 30.0
fillet_radius = 2.0
rib_width = 6.0
rib_height = 4.0
rib_offset_y = -bracket_width/2 + 10.0
counterbore_diameter = 8.0
counterbore_depth = 6.0

result = Box(bracket_length, bracket_width, bracket_thickness)
result = result + Pos(boss_offset_x, 0, bracket_thickness/2 + boss_height/2) * Cylinder(boss_diameter/2, boss_height)
result = fillet(result.edges().filter_by(Axis.Z), fillet_radius)
result = result - Pos(-hole_spacing/2, 0, 0) * Cylinder(hole_diameter/2, bracket_thickness + 2)
result = result - Pos(hole_spacing/2, 0, 0) * Cylinder(hole_diameter/2, bracket_thickness + 2)
result = result + Pos(0, rib_offset_y, -bracket_thickness/2 - rib_height/2) * Box(rib_width, rib_width, rib_height)
result = result - Pos(boss_offset_x, 0, bracket_thickness/2 + boss_height - counterbore_depth/2) * Cylinder(counterbore_diameter/2, counterbore_depth)

part = result
part.name = "bracket"
export_step(part, "output.step")