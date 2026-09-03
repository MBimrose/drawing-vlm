from build123d import *

circle_diameter = 20.0
rect_width = 30.0
rect_height = 45.0
bracket_thickness = 10.0
bracket_length = 40.0
rib_width = 8.0
rib_height = 12.0
rib_thickness = 5.0
rib_fillet = 0.5
hole_diameter = 5.0
hole_spacing = 15.0
hole_count = 3

with BuildPart() as p:
    with BuildSketch() as s1:
        Circle(circle_diameter / 2)
    with BuildSketch(Plane.XY.offset(bracket_length)) as s2:
        Rectangle(rect_width, rect_height)
    loft()

solid_body = p.part
rib = Pos(0, 0, bracket_length / 2) * Box(rib_width, rib_height, rib_thickness)
rib = fillet(rib.edges(), rib_fillet)
solid_body = solid_body + rib

for i in range(hole_count):
    x = (i - (hole_count - 1) / 2) * hole_spacing
    solid_body = solid_body - Pos(x, 0, bracket_length / 2) * Rot(90, 0, 0) * Cylinder(hole_diameter / 2, 100)

part = solid_body
part.name = "bracket_with_rib_and_holes"
export_step(part, "output.step")