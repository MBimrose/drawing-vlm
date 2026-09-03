from build123d import *

plate_width = 80.0
plate_depth = 60.0
plate_thickness = 6.0
boss_radius = 8.0
boss_height = 12.0
hole_diameter = 3.2
hole_offset = 10.0
chamfer_size = 1.0

base = Pos(0, 0, plate_thickness/2) * Box(plate_width, plate_depth, plate_thickness)
boss = Pos(0, 0, plate_thickness) * Cylinder(boss_radius, boss_height)
result = base + boss

for x, y in [(hole_offset, hole_offset), (plate_width - hole_offset, hole_offset),
             (hole_offset, plate_depth - hole_offset), (plate_width - hole_offset, plate_depth - hole_offset)]:
    result = result - Pos(x, y, 0) * Cylinder(hole_diameter/2, 30)

top_face = result.faces().sort_by(Axis.Z)[-1]
result = chamfer(top_face.edges(), chamfer_size)

part = result
part.name = "plate_with_boss_and_holes"
export_step(part, "output.step")