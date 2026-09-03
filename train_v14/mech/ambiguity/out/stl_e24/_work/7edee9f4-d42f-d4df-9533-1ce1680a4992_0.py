from build123d import *

plate_length = 80.0
plate_width = 60.0
plate_thickness = 6.0
boss_radius = 8.0
boss_height = 12.0
hole_diameter = 3.2
hole_offset = 10.0
chamfer_size = 1.0

base = Box(plate_length, plate_width, plate_thickness)
boss = Pos(0, 0, plate_thickness / 2) * Cylinder(boss_radius, boss_height)
solid_body = base + boss

hole_positions = [
    (hole_offset, hole_offset),
    (plate_length - hole_offset, hole_offset),
    (hole_offset, plate_width - hole_offset),
    (plate_length - hole_offset, plate_width - hole_offset),
]
for x, y in hole_positions:
    solid_body = solid_body - Pos(x, y, 0) * Cylinder(hole_diameter / 2, plate_thickness + boss_height + 10)

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = chamfer(top_face.edges(), chamfer_size)

part = solid_body
part.name = "plate_with_boss_and_holes"
export_step(part, "output.step")