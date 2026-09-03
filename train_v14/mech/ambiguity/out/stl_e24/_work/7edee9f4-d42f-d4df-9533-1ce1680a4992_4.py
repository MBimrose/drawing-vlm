from build123d import *

plate_length = 80.0
plate_width = 60.0
plate_thickness = 6.0
boss_radius = 8.0
boss_height = 12.0
hole_diameter = 3.2
hole_offset = 10.0
chamfer_distance = 1.0
rib_thickness = 4.0
rib_height = 3.0
rib_spacing = 20.0

base = Pos(0, 0, plate_thickness / 2) * Box(plate_length, plate_width, plate_thickness)
boss = Pos(0, 0, boss_height / 2) * Cylinder(boss_radius, boss_height)
result = base + boss

hole_positions = [
    (hole_offset, hole_offset),
    (plate_length - hole_offset, hole_offset),
    (hole_offset, plate_width - hole_offset),
    (plate_length - hole_offset, plate_width - hole_offset),
]
for x, y in hole_positions:
    result = result - Pos(x, y, boss_height / 2) * Cylinder(hole_diameter / 2, boss_height + 10)

top_face = result.faces().sort_by(Axis.Z)[-1]
result = chamfer(top_face.edges(), chamfer_distance)

rib_positions = [
    (rib_spacing, rib_spacing),
    (-rib_spacing, rib_spacing),
    (rib_spacing, -rib_spacing),
    (-rib_spacing, -rib_spacing),
]
for x, y in rib_positions:
    result = result + Pos(x, y, rib_height / 2) * Box(rib_thickness, rib_thickness, rib_height)

part = result
part.name = "plate_with_boss_and_ribs"
export_step(part, "output.step")