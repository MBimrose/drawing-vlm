from build123d import *

plate_length = 80.0
plate_width = 30.0
plate_thickness = 20.0
boss_diameter = 50.0
boss_height = 15.0
hole_diameter = 15.0
hole_spacing = 30.0
fillet_radius = 3.0
shell_thickness = 1.5

base = Box(plate_length, plate_width, plate_thickness)
boss = Cylinder(boss_diameter / 2, boss_height)
solid_body = base + boss

solid_body = solid_body - Cylinder(hole_diameter / 2, 100)
for x in [-hole_spacing, hole_spacing]:
    solid_body = solid_body - Pos(x, 0, 0) * Cylinder(hole_diameter / 2, 100)

solid_body = fillet(solid_body.edges(), fillet_radius)
solid_body = offset(solid_body, amount=-shell_thickness)

part = solid_body
part.name = "ShelledPlateWithBoss"
export_step(part, "output.step")