from build123d import *

plate_length = 80.0
plate_width = 50.0
plate_thickness = 8.0
boss_diameter = 30.0
boss_height = 12.0
hole_diameter = 5.0
hole_spacing = 15.0
hole_count = 5
chamfer_distance = 1.0
rib_height = 4.0
rib_width = 6.0
rib_spacing = 20.0

with BuildPart() as p:
    with BuildSketch() as s:
        Rectangle(plate_length, plate_width)
    extrude(amount=plate_thickness)
    with BuildSketch() as s2:
        Circle(boss_diameter / 2)
    extrude(amount=boss_height)

solid_body = p.part

rib1 = Pos(0, -rib_spacing / 2, plate_thickness + rib_height / 2) * Box(plate_length, rib_width, rib_height)
rib2 = Pos(0, rib_spacing / 2, plate_thickness + rib_height / 2) * Box(plate_length, rib_width, rib_height)
solid_body = solid_body + rib1 + rib2

for i in range(hole_count):
    x = (i - (hole_count - 1) / 2) * hole_spacing
    solid_body = solid_body - Pos(x, 0, 0) * Cylinder(hole_diameter / 2, 100)

vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = chamfer(vertical_edges, chamfer_distance)

part = solid_body
part.name = "plate_with_boss_ribs_and_holes"
export_step(part, "output.step")