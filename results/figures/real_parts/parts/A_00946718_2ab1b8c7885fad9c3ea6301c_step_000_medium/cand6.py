from build123d import *

plate_length = 80.0
plate_width = 30.0
plate_thickness = 20.0
boss_diameter = 50.0
boss_height = plate_thickness
wall_thickness = 1.5
central_hole_diameter = 20.0
side_hole_diameter = 10.0
side_hole_spacing = 40.0
fillet_radius = 2.7

base_plate = Box(plate_length, plate_width, plate_thickness)
boss = Cylinder(boss_diameter / 2, boss_height)
solid_body = base_plate + boss

solid_body = offset(solid_body, amount=-wall_thickness)

solid_body = solid_body - Cylinder(central_hole_diameter / 2, plate_thickness * 2)
for x in [-side_hole_spacing / 2, side_hole_spacing / 2]:
    solid_body = solid_body - Pos(x, 0, 0) * Cylinder(side_hole_diameter / 2, plate_thickness * 2)

solid_body = fillet(solid_body.edges(), fillet_radius)

part = solid_body
part.name = "plated_boss_with_holes"
export_step(part, "output.step")