from build123d import *

plate_length = 80.0
plate_width = 30.0
plate_thickness = 15.0
boss_diameter = 45.0
hole_diameter = 12.0
hole_spacing = 55.0
fillet_radius = 2.0
slot_width = 8.0
slot_length = 20.0

base = Box(plate_length, plate_width, plate_thickness)
boss = Cylinder(boss_diameter / 2, plate_thickness)
result = base + boss

result = result - Cylinder(hole_diameter / 2, plate_thickness * 2)

for x in [-hole_spacing / 2, hole_spacing / 2]:
    result = result - Pos(x, 0, 0) * Cylinder(hole_diameter / 2, plate_thickness * 2)

for x in [-plate_length / 2 + slot_length / 2, plate_length / 2 - slot_length / 2]:
    result = result - Pos(x, 0, 0) * Box(slot_length, slot_width, plate_thickness * 2)

result = fillet(result.edges(), fillet_radius)

part = result
part.name = "plate_with_boss_holes_slots"
export_step(part, "output.step")