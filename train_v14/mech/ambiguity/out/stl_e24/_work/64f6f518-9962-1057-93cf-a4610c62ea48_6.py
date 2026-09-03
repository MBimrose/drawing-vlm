from build123d import *

plate_length = 45.0
plate_width = 30.0
plate_thickness = 10.0
boss_diameter = 15.0
boss_height = 10.0
hole_diameter = 5.0
hole_spacing = 15.0
hole_count = 3
fillet_radius = 2.0

with BuildPart() as p:
    with BuildSketch() as s1:
        Rectangle(plate_width, plate_thickness)
    with BuildSketch(Plane.XY.offset(plate_length)) as s2:
        Rectangle(plate_width, plate_thickness)
    loft()

solid_body = p.part
solid_body = solid_body + Pos(-plate_width/2, 0, plate_length/2) * Cylinder(boss_diameter/2, plate_length)

for i in range(hole_count):
    x = (i - (hole_count-1)/2) * hole_spacing
    solid_body = solid_body - Pos(x, 0, plate_length/2) * Rot(90, 0, 0) * Cylinder(hole_diameter/2, plate_thickness + 10)

solid_body = fillet(solid_body.edges().filter_by(Axis.Z), fillet_radius)

part = solid_body
part.name = "plate_with_boss_and_holes"
export_step(part, "output.step")