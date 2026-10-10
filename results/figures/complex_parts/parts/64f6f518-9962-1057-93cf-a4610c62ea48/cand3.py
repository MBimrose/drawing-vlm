from build123d import *

circle_diameter = 10.0
rect_width = 30.0
rect_height = 8.0
loft_length = 45.0
hole_diameter = 5.0
hole_spacing = 15.0
hole_count = 3
chamfer_distance = 1.0

with BuildPart() as p:
    with BuildSketch() as s1:
        Circle(circle_diameter / 2)
    with BuildSketch(Plane.XY.offset(loft_length)) as s2:
        Rectangle(rect_width, rect_height)
    loft()

solid_body = p.part

for i in range(hole_count):
    x = (i - (hole_count - 1) / 2) * hole_spacing
    solid_body = solid_body - Pos(x, 0, loft_length / 2) * Rot(90, 0, 0) * Cylinder(hole_diameter / 2, rect_height + 2)

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
top_edges = top_face.edges()
solid_body = chamfer(top_edges, chamfer_distance)

part = solid_body
part.name = "lofted_part_with_holes"
export_step(part, "output.step")