from build123d import *

circle_diameter = 60.0
rect_width = 40.0
rect_height = 20.0
loft_height = 60.0
chamfer_distance = 2.0
hole_diameter = 4.0
hole_spacing = 25.0
hole_offset_y = 15.0
pocket_width = 20.0
pocket_height = 8.0
pocket_depth = 10.0

with BuildPart() as p:
    with BuildSketch() as s1:
        Circle(circle_diameter / 2)
    with BuildSketch(Plane.XY.offset(loft_height)) as s2:
        Rectangle(rect_width, rect_height)
    loft()

solid_body = p.part

pocket = Box(pocket_width, pocket_height, pocket_depth)
solid_body = solid_body - Pos(0, 0, loft_height - pocket_depth / 2) * pocket

for x, y in [(-hole_spacing / 2, hole_offset_y), (hole_spacing / 2, hole_offset_y)]:
    solid_body = solid_body - Pos(x, y, loft_height / 2) * Cylinder(hole_diameter / 2, loft_height + 10)

vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = chamfer(vertical_edges, chamfer_distance)

part = solid_body
part.name = "lofted_body_with_pocket_and_holes"
export_step(part, "output.step")