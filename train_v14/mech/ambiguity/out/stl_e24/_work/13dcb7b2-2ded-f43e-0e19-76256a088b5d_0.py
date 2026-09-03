from build123d import *

plate_length = 80.0
plate_width = 60.0
plate_thickness = 5.0
rib_height = 3.0
rib_thickness = 4.0
boss_diameter = 12.0
boss_height = 8.0
boss_spacing_x = 30.0
boss_spacing_y = 30.0
hole_diameter = 6.0
hole_spacing = 16.0
chamfer_size = 0.5
pocket_depth = 2.0
pocket_margin = 5.0

with BuildPart() as p:
    with BuildSketch() as s1:
        Rectangle(plate_length, plate_width)
    with BuildSketch(Plane.XY.offset(plate_thickness)) as s2:
        Rectangle(plate_length - 2 * rib_thickness, plate_width - 2 * rib_thickness)
    loft()

solid_body = p.part
solid_body = solid_body + Pos(0, 0, plate_thickness + rib_height / 2) * Box(plate_length - 2 * rib_thickness, plate_width - 2 * rib_thickness, rib_height)

boss_positions = [
    (boss_spacing_x / 2, boss_spacing_y / 2),
    (-boss_spacing_x / 2, boss_spacing_y / 2),
    (boss_spacing_x / 2, -boss_spacing_y / 2),
    (-boss_spacing_x / 2, -boss_spacing_y / 2),
]
for x, y in boss_positions:
    solid_body = solid_body + Pos(x, y, plate_thickness + boss_height / 2) * Cylinder(boss_diameter / 2, boss_height)

solid_body = solid_body - Pos(0, 0, plate_thickness + rib_height - pocket_depth / 2) * Box(plate_length - 2 * pocket_margin, plate_width - 2 * pocket_margin, pocket_depth)

hole_positions = [
    (hole_spacing / 2, hole_spacing / 2),
    (-hole_spacing / 2, hole_spacing / 2),
    (hole_spacing / 2, -hole_spacing / 2),
    (-hole_spacing / 2, -hole_spacing / 2),
]
for x, y in hole_positions:
    solid_body = solid_body - Pos(x, y, (plate_thickness + boss_height) / 2) * Cylinder(hole_diameter / 2, plate_thickness + boss_height + 10)

for x, y in boss_positions:
    solid_body = solid_body - Pos(x, y, (plate_thickness + boss_height) / 2) * Cylinder(hole_diameter / 2, plate_thickness + boss_height + 10)

solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_size)

part = solid_body
part.name = "plate_with_ribs_bosses_and_holes"
export_step(part, "output.step")