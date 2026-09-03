from build123d import *

bracket_length = 70.0
bracket_width = 40.0
bracket_thickness = 8.0
boss_diameter = 20.0
boss_height = 12.0
boss_offset = 15.0
blind_hole_diameter = 8.0
blind_hole_depth = 6.0
fillet_radius = 2.0
mount_hole_diameter = 6.0
mount_hole_spacing = 30.0
rib_width = 6.0
rib_height = 4.0
rib_offset = 10.0

base = Box(bracket_length, bracket_width, bracket_thickness)
base = fillet(base.edges().filter_by(Axis.Z), fillet_radius)

boss_center_x = -bracket_length/2 + boss_offset
boss = Pos(boss_center_x, 0, bracket_thickness/2 + boss_height/2) * Cylinder(boss_diameter/2, boss_height)
blind_hole = Pos(boss_center_x, 0, bracket_thickness/2 + boss_height - blind_hole_depth/2) * Cylinder(blind_hole_diameter/2, blind_hole_depth)

result = base + boss - blind_hole

for x in [-mount_hole_spacing/2, mount_hole_spacing/2]:
    result = result - Pos(x, 0, 0) * Cylinder(mount_hole_diameter/2, bracket_thickness)

rib_center_y = -bracket_width/2 + rib_offset + rib_width/2
rib = Pos(0, rib_center_y, -bracket_thickness/2 - rib_height/2) * Box(rib_width, rib_width, rib_height)
result = result + rib

part = result
part.name = "bracket"
export_step(part, "output.step")