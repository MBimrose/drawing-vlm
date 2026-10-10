from build123d import *

plate_length = 80.0
plate_width = 30.0
plate_thickness = 15.0
boss_diameter = 45.0
boss_thickness = plate_thickness
hole_diameter = 15.0
hole_spacing = 40.0
fillet_radius = 2.5
pocket_length = 20.0
pocket_width = 10.0
pocket_depth = 5.0

base = Box(plate_length, plate_width, plate_thickness)
boss = Cylinder(boss_diameter / 2, boss_thickness)
solid_body = base + boss

solid_body = solid_body - Cylinder((boss_diameter - 10) / 2, boss_thickness)

for x in [-hole_spacing / 2, hole_spacing / 2]:
    solid_body = solid_body - Pos(x, 0, 0) * Cylinder(hole_diameter / 2, plate_thickness)

solid_body = fillet(solid_body.edges(), fillet_radius)

pocket = Pos(0, 0, plate_thickness - pocket_depth / 2) * Box(pocket_length, pocket_width, pocket_depth)
solid_body = solid_body - pocket

part = solid_body
part.name = "plate_with_boss_and_pocket"
export_step(part, "output.step")