from build123d import *

bracket_length = 70.0
bracket_width = 40.0
bracket_thickness = 8.0
boss_diameter = 20.0
boss_height = 12.0
boss_offset_x = -bracket_length/2 + 15.0
boss_offset_y = 0.0
fillet_radius = 2.0
mount_hole_diameter = 6.0
mount_hole_spacing = 30.0
mount_hole_offset_y = 0.0
rib_width = 6.0
rib_height = 4.0
rib_offset_y = -bracket_width/4
pocket_width = 10.0
pocket_depth = 4.0
pocket_offset_x = 0.0
pocket_offset_y = 0.0

base = Pos(0, 0, bracket_thickness/2) * Box(bracket_length, bracket_width, bracket_thickness)
base = fillet(base.edges().filter_by(Axis.Z), fillet_radius)

boss = Pos(boss_offset_x, boss_offset_y, bracket_thickness + boss_height/2) * Cylinder(boss_diameter/2, boss_height)
result = base + boss

hole = Pos(boss_offset_x, boss_offset_y, bracket_thickness + boss_height/2) * Cylinder(boss_diameter/2 * 0.8 / 2, boss_height + bracket_thickness)
result = result - hole

for x in [-mount_hole_spacing/2, mount_hole_spacing/2]:
    result = result - Pos(x, mount_hole_offset_y, bracket_thickness/2) * Cylinder(mount_hole_diameter/2, bracket_thickness + 1)

rib = Pos(0, rib_offset_y, -rib_height/2) * Box(rib_width, rib_width, rib_height)
result = result + rib

pocket = Pos(pocket_offset_x, pocket_offset_y, bracket_thickness + boss_height - pocket_depth/2) * Box(pocket_width, pocket_depth, pocket_depth)
result = result - pocket

part = result
part.name = "bracket"
export_step(part, "output.step")