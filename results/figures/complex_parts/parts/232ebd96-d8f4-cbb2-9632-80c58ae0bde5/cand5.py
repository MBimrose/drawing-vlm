from build123d import *

leg_length = 80.0
leg_width = 15.0
thickness = 8.0
boss_diameter = 30.0
boss_height = 20.0
through_hole_diameter = 10.0
mount_hole_diameter = 5.0
mount_hole_spacing = 30.0
relief_width = 20.0
relief_depth = 6.0
chamfer_size = 1.0

horizontal_leg = Pos(leg_length/2, leg_width/2, thickness/2) * Box(leg_length, leg_width, thickness)
vertical_leg = Pos(leg_width/2, leg_length/2, thickness/2) * Box(leg_width, leg_length, thickness)
base = horizontal_leg + vertical_leg

boss = Pos(leg_width, leg_width, thickness + boss_height/2) * Cylinder(boss_diameter/2, boss_height)
result = base + boss

through_hole = Pos(leg_width, leg_width, (thickness + boss_height)/2) * Cylinder(through_hole_diameter/2, thickness + boss_height)
result = result - through_hole

for i in range(2):
    y = leg_width + mount_hole_spacing/2 + i * mount_hole_spacing
    result = result - Pos(0, y, thickness/2) * Cylinder(mount_hole_diameter/2, thickness)

for i in range(2):
    x = leg_width + mount_hole_spacing/2 + i * mount_hole_spacing
    result = result - Pos(x, 0, thickness/2) * Cylinder(mount_hole_diameter/2, thickness)

relief = Pos(leg_length - relief_width/2, leg_width/2, thickness/2) * Box(relief_width, relief_depth, thickness)
result = result - relief

result = chamfer(result.edges(), chamfer_size)

part = result
part.name = "L_bracket"
export_step(part, "output.step")