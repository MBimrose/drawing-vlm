from build123d import *

hub_diameter = 80.0
hub_width = 25.0
boss_diameter = 30.0
boss_height = 20.0
bore_diameter = 12.0
fillet_radius = 3.0
mount_hole_diameter = 5.0
mount_hole_offset = 25.0
mount_hole_angle = 45.0
rib_thickness = 4.0
rib_height = 6.0
rib_spacing = 30.0

hub_body = Pos(0, 0, hub_width/2) * Cylinder(hub_diameter/2, hub_width)
boss_body = Pos(0, 0, -boss_height/2) * Cylinder(boss_diameter/2, boss_height)
result = hub_body + boss_body
result = fillet(result.edges(), fillet_radius)
result = result - Cylinder(bore_diameter/2, 100)
import math
for sign in (1, -1):
    px = mount_hole_offset * math.cos(math.radians(mount_hole_angle)) * sign
    py = mount_hole_offset * math.sin(math.radians(mount_hole_angle))
    result = result - Pos(px, py, 0) * Cylinder(mount_hole_diameter/2, 100)
rib1 = Pos(-rib_spacing/2, 0, rib_height/2) * Box(rib_thickness, rib_height, rib_height)
rib2 = Pos(rib_spacing/2, 0, rib_height/2) * Box(rib_thickness, rib_height, rib_height)
result = result + rib1 + rib2
part = result
part.name = "hub_with_boss_and_ribs"
export_step(part, "output.step")