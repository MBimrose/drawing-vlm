from build123d import *

leg_length_x = 80.0
leg_length_y = 70.0
leg_width = 15.0
thickness = 8.0
boss_diameter = 30.0
boss_height = 20.0
through_hole_diameter = 10.0
mount_hole_diameter = 5.0
mount_hole_spacing = 40.0

horiz = Pos(leg_length_x/2, leg_width/2, thickness/2) * Box(leg_length_x, leg_width, thickness)
vert = Pos(leg_width/2, leg_length_y/2 + leg_width, thickness/2) * Box(leg_width, leg_length_y, thickness)
base = horiz + vert

boss = Pos(leg_width, leg_width, thickness + boss_height/2) * Cylinder(boss_diameter/2, boss_height)
base = base + boss

through_hole = Pos(leg_width, leg_width, (thickness + boss_height)/2) * Cylinder(through_hole_diameter/2, thickness + boss_height)
base = base - through_hole

for i in range(2):
    x = leg_length_x/2 + i * mount_hole_spacing
    base = base - Pos(x, 0, thickness/2) * Cylinder(mount_hole_diameter/2, thickness)

for i in range(2):
    y = leg_width + leg_length_y/2 + i * mount_hole_spacing
    base = base - Pos(0, y, thickness/2) * Cylinder(mount_hole_diameter/2, thickness)

part = base
part.name = "L_Bracket"
export_step(part, "output.step")