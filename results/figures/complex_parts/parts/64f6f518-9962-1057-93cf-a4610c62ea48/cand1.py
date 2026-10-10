from build123d import *

circle_diameter = 10.0
rect_width = 30.0
rect_height = 45.0
loft_length = 45.0
hole_diameter = 5.0
hole_depth = 12.0
hole_spacing_x = 15.0
hole_spacing_y = 15.0
hole_rows = 2
hole_cols = 3

with BuildPart() as p:
    with BuildSketch() as s1:
        Circle(circle_diameter / 2)
    with BuildSketch(Plane.XY.offset(loft_length)) as s2:
        Rectangle(rect_width, rect_height)
    loft()

solid_body = p.part

for i in range(hole_cols):
    for j in range(hole_rows):
        x = (i - (hole_cols - 1) / 2) * hole_spacing_x
        z = (j - (hole_rows - 1) / 2) * hole_spacing_y
        hole = Pos(x, rect_height / 2 - hole_depth / 2, z) * Rot(90, 0, 0) * Cylinder(hole_diameter / 2, hole_depth)
        solid_body = solid_body - hole

part = solid_body
part.name = "lofted_part_with_holes"
export_step(part, "output.step")