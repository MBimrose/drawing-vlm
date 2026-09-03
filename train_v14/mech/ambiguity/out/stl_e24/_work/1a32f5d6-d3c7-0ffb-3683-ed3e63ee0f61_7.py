from build123d import *

plate_width = 80.0
plate_depth = 60.0
plate_thickness = 6.0
boss_across_flats = 50.0
boss_height = 4.0
hole_diameter = 6.0
countersink_diameter = 12.0
countersink_angle = 82.0
hole_spacing_x = 20.0
hole_spacing_y = 20.0
num_holes_x = 4
num_holes_y = 3
chamfer_size = 1.0

with BuildPart() as p:
    Box(plate_width, plate_depth, plate_thickness)
    with BuildSketch() as s:
        RegularPolygon(boss_across_flats, 6)
    extrude(amount=boss_height)

solid_body = p.part

for i in range(num_holes_x):
    for j in range(num_holes_y):
        x = (i - (num_holes_x - 1) / 2) * hole_spacing_x
        y = (j - (num_holes_y - 1) / 2) * hole_spacing_y
        solid_body = solid_body - Pos(x, y, plate_thickness / 2) * CounterSinkHole(hole_diameter / 2, countersink_diameter / 2, plate_thickness, countersink_angle)

solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_size)

part = solid_body
part.name = "plate_with_hex_boss_and_holes"
export_step(part, "output.step")