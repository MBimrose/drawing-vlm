from build123d import *

arm_length = 45.0
circle_diameter = 10.0
rect_width = 30.0
rect_height = 8.0
hole_diameter = 5.0
hole_spacing = 15.0
hole_count = 3

with BuildPart() as p:
    with BuildSketch() as s1:
        Circle(circle_diameter / 2)
    with BuildSketch(Plane.XY.offset(arm_length)) as s2:
        Rectangle(rect_width, rect_height)
    loft()

solid_body = p.part

for i in range(hole_count):
    x = (i - (hole_count - 1) / 2) * hole_spacing
    solid_body = solid_body - Pos(x, 0, arm_length / 2) * Rot(90, 0, 0) * Cylinder(hole_diameter / 2, arm_length + 10)

part = solid_body
part.name = "lofted_arm_with_holes"
export_step(part, "output.step")