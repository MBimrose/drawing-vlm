from build123d import *

circle_diameter = 10.0
rect_width = 30.0
rect_height = 8.0
loft_length = 45.0
fillet_radius = 2.0
hole_diameter = 5.0
hole_spacing = 15.0
notch_width = 6.0
notch_depth = 3.0

circle_radius = 0.5 * circle_diameter
rect_center_x = circle_radius + 0.5 * rect_width

with BuildPart() as p:
    with BuildSketch() as s1:
        Circle(circle_radius)
    with BuildSketch(Plane.XY.offset(loft_length)) as s2:
        Pos(rect_center_x, 0, 0) * Rectangle(rect_width, rect_height)
    loft()

solid_body = p.part

z_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = fillet(z_edges, fillet_radius)

notch = Pos(circle_radius + notch_depth / 2, 0, loft_length / 2) * Box(notch_depth, notch_width, loft_length)
solid_body = solid_body - notch

for i in range(3):
    x_pos = rect_center_x + (i - 1) * hole_spacing
    hole = Pos(x_pos, 0, loft_length / 2) * Rot(90, 0, 0) * Cylinder(hole_diameter / 2, rect_height + 2)
    solid_body = solid_body - hole

part = solid_body
part.name = "lofted_circle_to_rect_with_notch_and_holes"
export_step(part, "output.step")