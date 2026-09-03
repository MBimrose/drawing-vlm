from build123d import *

plate_length = 80.0
plate_width = 60.0
plate_thickness = 5.0
boss_diameter = 12.0
boss_height = 15.0
boss_spacing_x = 30.0
boss_spacing_y = 25.0
hole_diameter = 6.0
chamfer_size = 1.0
rib_width = 10.0
rib_height = 3.0
rib_length = 40.0

with BuildPart() as p:
    with BuildSketch() as s1:
        Rectangle(plate_length, plate_width)
    with BuildSketch(Plane.XY.offset(plate_thickness)) as s2:
        Rectangle(plate_length - 10, plate_width - 10)
    loft()

solid_body = p.part
solid_body = chamfer(solid_body.edges(), chamfer_size)

rib = Pos(0, 0, rib_height / 2) * Box(rib_length, rib_width, rib_height)
solid_body = solid_body + rib

boss_positions = [
    (-boss_spacing_x / 2, -boss_spacing_y / 2),
    (boss_spacing_x / 2, -boss_spacing_y / 2),
    (-boss_spacing_x / 2, boss_spacing_y / 2),
    (boss_spacing_x / 2, boss_spacing_y / 2),
]

for x, y in boss_positions:
    boss = Pos(x, y, boss_height / 2) * Cylinder(boss_diameter / 2, boss_height)
    solid_body = solid_body + boss

for x, y in boss_positions:
    hole = Pos(x, y, (boss_height + plate_thickness) / 2) * Cylinder(hole_diameter / 2, boss_height + plate_thickness)
    solid_body = solid_body - hole

part = solid_body
part.name = "plate_with_bosses_and_rib"
export_step(part, "output.step")