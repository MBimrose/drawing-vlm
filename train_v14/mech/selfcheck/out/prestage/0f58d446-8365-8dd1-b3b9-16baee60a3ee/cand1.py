from build123d import *
import math

bracket_length = 70.0
bracket_width = 40.0
bracket_thickness = 8.0
boss_diameter = 20.0
boss_height = 12.0
boss_offset_from_end = 15.0
mount_hole_diameter = 6.0
mount_hole_spacing = 30.0
counterbore_diameter = 8.0
counterbore_depth = 6.0
countersink_angle = 90.0
fillet_radius = 2.0
rib_width = 6.0
rib_height = 4.0
rib_offset_y = 10.0

base = Box(bracket_length, bracket_width, bracket_thickness)
base = fillet(base.edges().filter_by(Axis.Z), fillet_radius)

boss_center_x = -bracket_length/2 + boss_offset_from_end
boss = Pos(boss_center_x, 0, bracket_thickness/2 + boss_height/2) * Cylinder(boss_diameter/2, boss_height)

rib = Pos(0, -bracket_width/2 + rib_offset_y, -bracket_thickness/2 - rib_height/2) * Box(rib_width, rib_width, rib_height)

result = base + boss + rib

for x in [-mount_hole_spacing/2, mount_hole_spacing/2]:
    result = result - Pos(x, 0, 0) * Cylinder(mount_hole_diameter/2, bracket_thickness + 2)

csk_radius = counterbore_diameter/2 + counterbore_depth * math.tan(math.radians(countersink_angle/2))
csk_cone = Pos(boss_center_x, 0, bracket_thickness/2 + boss_height - counterbore_depth/2) * Cone(counterbore_diameter/2, csk_radius, counterbore_depth)
shaft_cyl = Pos(boss_center_x, 0, bracket_thickness/2 + boss_height - counterbore_depth - (boss_height - counterbore_depth)/2) * Cylinder(counterbore_diameter/2, boss_height - counterbore_depth)
result = result - csk_cone - shaft_cyl

part = result
part.name = "bracket"
export_step(part, "output.step")