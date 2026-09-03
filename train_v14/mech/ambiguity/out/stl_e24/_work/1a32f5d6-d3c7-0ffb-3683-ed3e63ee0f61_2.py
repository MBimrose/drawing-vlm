from build123d import *

plate_length = 80.0
plate_width = 60.0
plate_thickness = 6.0
hex_outer_radius = 30.0
hex_inner_radius = 25.0
hole_diameter = 6.0
countersink_diameter = 12.0
countersink_angle = 82.0
hole_spacing_x = 20.0
hole_spacing_y = 40.0
chamfer_distance = 0.5
boss_height = 2.0
boss_radius = 8.0

with BuildPart() as p:
    with BuildSketch() as s:
        Rectangle(plate_length, plate_width)
    extrude(amount=plate_thickness)

with BuildPart() as boss_p:
    with BuildSketch() as bs:
        RegularPolygon(boss_radius, 6)
    extrude(amount=boss_height)

solid_body = p.part + boss_p.part

with BuildPart() as cut_p:
    with BuildSketch(Plane.XY.offset(plate_thickness)) as cs:
        RegularPolygon(hex_outer_radius, 6)
        RegularPolygon(hex_inner_radius, 6, mode=Mode.SUBTRACT)
    extrude(amount=-plate_thickness)

solid_body = solid_body - cut_p.part

for i in range(4):
    for j in range(2):
        x = (i - 1.5) * hole_spacing_x
        y = (j - 0.5) * hole_spacing_y
        solid_body = solid_body - Pos(x, y, plate_thickness) * CounterSinkHole(hole_diameter/2, countersink_diameter/2, plate_thickness, countersink_angle)

solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_distance)

part = solid_body
part.name = "hex_plate_with_boss"
export_step(part, "output.step")