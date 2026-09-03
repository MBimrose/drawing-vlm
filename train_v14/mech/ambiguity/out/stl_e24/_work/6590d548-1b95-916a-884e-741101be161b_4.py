from build123d import *

base_radius = 30.0
top_width = 40.0
top_height = 20.0
total_length = 60.0
pocket_width = 20.0
pocket_depth = 8.0
pocket_height = 10.0
fillet_radius = 2.0
hole_diameter = 4.0
hole_spacing = 25.0
hole_offset_y = 15.0

with BuildPart() as p:
    with BuildSketch() as s1:
        Circle(base_radius)
    with BuildSketch(Plane.XY.offset(total_length)) as s2:
        Rectangle(top_width, top_height)
    loft()

solid_body = p.part

pocket = Pos(0, 0, total_length - pocket_height / 2) * Box(pocket_width, pocket_depth, pocket_height)
solid_body = solid_body - pocket

for x in [-hole_spacing / 2, hole_spacing / 2]:
    hole = Pos(x, hole_offset_y, total_length / 2) * Cylinder(hole_diameter / 2, total_length + 10)
    solid_body = solid_body - hole

vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = fillet(vertical_edges, fillet_radius)

part = solid_body
part.name = "lofted_body_with_pocket_and_holes"
export_step(part, "output.step")