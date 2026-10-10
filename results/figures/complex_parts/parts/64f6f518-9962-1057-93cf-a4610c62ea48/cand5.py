from build123d import *

boss_radius = 5.0
boss_height = 45.0
plate_width = 30.0
plate_height = 45.0
plate_thickness = 6.0
hole_diameter = 5.0
hole_spacing = 15.0
hole_count = 3
chamfer_size = 0.8

with BuildPart() as p:
    with BuildSketch() as s1:
        Circle(boss_radius)
    with BuildSketch(Plane.XY.offset(boss_height)) as s2:
        Rectangle(plate_width, plate_thickness)
    loft()

solid_body = p.part

for i in range(hole_count):
    x = (i - (hole_count - 1) / 2) * hole_spacing
    solid_body = solid_body - Pos(x, 0, boss_height / 2) * Rot(90, 0, 0) * Cylinder(hole_diameter / 2, plate_thickness + 20)

solid_body = chamfer(solid_body.edges(), chamfer_size)

part = solid_body
part.name = "lofted_boss_plate"
export_step(part, "output.step")