from build123d import *

vertical_height = 70.0
horizontal_length = 80.0
leg_width = 20.0
bracket_thickness = 8.0
gusset_length = 30.0
gusset_thickness = 4.0
hole_diameter = 5.0
hole_spacing = 20.0
chamfer_size = 1.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            l1 = Line((0, 0), (0, vertical_height))
            l2 = Line(l1 @ 1, (leg_width, vertical_height))
            l3 = Line(l2 @ 1, (leg_width, leg_width))
            l4 = Line(l3 @ 1, (horizontal_length, leg_width))
            l5 = Line(l4 @ 1, (horizontal_length, 0))
            l6 = Line(l5 @ 1, (0, 0))
        make_face()
    extrude(amount=bracket_thickness)

solid_body = p.part

with BuildPart() as g:
    with BuildSketch() as gsk:
        with BuildLine() as gbl:
            gl1 = Line((leg_width, leg_width), (leg_width + gusset_length, leg_width))
            gl2 = Line(gl1 @ 1, (leg_width, leg_width + gusset_length))
            gl3 = Line(gl2 @ 1, (leg_width, leg_width))
        make_face()
    extrude(amount=gusset_thickness)

solid_body = solid_body + g.part

for x, y in [(leg_width / 2, vertical_height / 2 - hole_spacing / 2),
             (leg_width / 2, vertical_height / 2 + hole_spacing / 2)]:
    solid_body = solid_body - Pos(x, y, 0) * Cylinder(hole_diameter / 2, bracket_thickness + 10)

x_face = solid_body.faces().sort_by(Axis.X)[0]
y_face = solid_body.faces().sort_by(Axis.Y)[0]
common_edges = [e for e in x_face.edges() if e in y_face.edges()]
solid_body = chamfer(common_edges, chamfer_size)

part = solid_body
part.name = "L_Bracket"
export_step(part, "output.step")