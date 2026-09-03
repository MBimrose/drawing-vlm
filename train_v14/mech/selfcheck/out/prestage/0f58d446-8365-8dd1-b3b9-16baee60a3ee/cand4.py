from build123d import *

bracket_length = 70.0
bracket_width = 40.0
bracket_thickness = 8.0
boss_diameter = 20.0
boss_height = 12.0
boss_offset_from_end = 15.0
hole_diameter = 6.0
hole_spacing = 30.0
fillet_radius = 2.0
chamfer_distance = 1.0
rib_width = 6.0
rib_height = 4.0
rib_offset = 10.0
blind_hole_diameter = 8.0
blind_hole_depth = 6.0
pocket_width = 10.0
pocket_depth = 4.0
pocket_height = 3.0

boss_center_x = -bracket_length/2 + boss_offset_from_end

result = Box(bracket_length, bracket_width, bracket_thickness)
result = fillet(result.edges().filter_by(Axis.Z), fillet_radius)

boss = Pos(boss_center_x, 0, bracket_thickness/2 + boss_height/2) * Cylinder(boss_diameter/2, boss_height)
result = result + boss

for x in [-hole_spacing/2, hole_spacing/2]:
    result = result - Pos(x, 0, 0) * Cylinder(hole_diameter/2, 100)

result = result - Pos(boss_center_x, 0, bracket_thickness/2 + boss_height - blind_hole_depth/2) * Cylinder(blind_hole_diameter/2, blind_hole_depth)

result = result - Pos(boss_center_x, 0, bracket_thickness/2 + boss_height - pocket_height/2) * Box(pocket_width, pocket_depth, pocket_height)

rib = Pos(0, -bracket_width/2 + rib_offset, -bracket_thickness/2 - rib_height/2) * Box(rib_width, rib_width, rib_height)
result = result + rib

top_face = result.faces().sort_by(Axis.Z)[-1]
result = chamfer(top_face.edges(), chamfer_distance)

part = result
part.name = "bracket"
export_step(part, "output.step")