from build123d import *

plate_length = 80.0
plate_width = 60.0
plate_thickness = 5.0
rim_height = 4.0
rim_thickness = 2.0
boss_diameter = 12.0
boss_height = 10.0
boss_hole_diameter = 6.0
boss_offset_x = 15.0
boss_offset_y = 12.0
chamfer_size = 1.0

with BuildPart() as p:
    with BuildSketch() as s1:
        Rectangle(plate_length, plate_width)
    with BuildSketch(Plane.XY.offset(plate_thickness)) as s2:
        Rectangle(plate_length - 2 * rim_thickness, plate_width - 2 * rim_thickness)
    loft()

solid_body = p.part
solid_body = chamfer(solid_body.edges(), chamfer_size)

boss_positions = [
    (boss_offset_x, boss_offset_y),
    (-boss_offset_x, boss_offset_y),
    (-boss_offset_x, -boss_offset_y),
    (boss_offset_x, -boss_offset_y),
]

for x, y in boss_positions:
    solid_body = solid_body + Pos(x, y, plate_thickness + boss_height / 2) * Cylinder(boss_diameter / 2, boss_height)

for x, y in boss_positions:
    solid_body = solid_body - Pos(x, y, (plate_thickness + boss_height) / 2) * Cylinder(boss_hole_diameter / 2, plate_thickness + boss_height + 10)

part = solid_body
part.name = "plate_with_rim_and_bosses"
export_step(part, "output.step")