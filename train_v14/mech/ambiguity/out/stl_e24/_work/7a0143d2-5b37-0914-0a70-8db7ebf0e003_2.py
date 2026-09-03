from build123d import *

vertical_height = 70.0
horizontal_length = 80.0
thickness = 10.0
notch_width = 5.0
notch_depth = 5.0
hole_diameter = 5.0
hole_offset = 20.0
chamfer_distance = 1.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            l1 = Line((0, 0), (thickness, 0))
            l2 = Line(l1@1, (thickness, vertical_height - thickness))
            l3 = Line(l2@1, (horizontal_length, vertical_height - thickness))
            l4 = Line(l3@1, (horizontal_length, vertical_height))
            l5 = Line(l4@1, (0, vertical_height))
            l6 = Line(l5@1, (0, 0))
        make_face()
    extrude(amount=thickness)

solid_body = p.part

notch = Pos(horizontal_length / 2, vertical_height - notch_depth / 2, thickness / 2) * Box(notch_width, notch_depth, thickness)
solid_body = solid_body - notch

for x, z in [(hole_offset, thickness / 2), (horizontal_length - hole_offset, thickness / 2)]:
    hole = Pos(x, vertical_height, z) * Rot(90, 0, 0) * Cylinder(hole_diameter / 2, 200)
    solid_body = solid_body - hole

bottom_edges = solid_body.edges().sort_by(Axis.Y)[:1]
solid_body = chamfer(bottom_edges, chamfer_distance)

part = solid_body
part.name = "L_Bracket"
export_step(part, "output.step")