from build123d import *

vertical_leg_length = 60.0
horizontal_leg_length = 70.0
leg_width = 30.0
thickness = 8.0
gusset_thickness = 8.0
hole_diameter = 6.0
cbore_diameter = 10.0
cbore_depth = 3.0
fillet_radius = 2.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            l1 = Line((0, 0), (leg_width, 0))
            l2 = Line(l1 @ 1, (leg_width, vertical_leg_length))
            l3 = Line(l2 @ 1, (leg_width + horizontal_leg_length, vertical_leg_length))
            l4 = Line(l3 @ 1, (leg_width + horizontal_leg_length, vertical_leg_length + leg_width))
            l5 = Line(l4 @ 1, (0, vertical_leg_length + leg_width))
            l6 = Line(l5 @ 1, (0, 0))
        make_face()
    extrude(amount=thickness)

solid_body = p.part
inner_edges = solid_body.edges().filter_by(Axis.Z).sort_by(Axis.X)[2:4]
solid_body = fillet(inner_edges, fillet_radius)

with BuildPart() as g:
    with BuildSketch() as gsk:
        with BuildLine() as gbl:
            gl1 = Line((leg_width, vertical_leg_length), (leg_width + gusset_thickness, vertical_leg_length))
            gl2 = Line(gl1 @ 1, (leg_width, vertical_leg_length + gusset_thickness))
            gl3 = Line(gl2 @ 1, (leg_width, vertical_leg_length))
        make_face()
    extrude(amount=thickness)

solid_body = solid_body + g.part

hole_positions = [
    (leg_width / 2, vertical_leg_length * 0.25),
    (leg_width / 2, vertical_leg_length * 0.75),
]

for x, y in hole_positions:
    solid_body = solid_body - Pos(x, y, thickness / 2) * Cylinder(hole_diameter / 2, thickness)
    solid_body = solid_body - Pos(x, y, thickness - cbore_depth / 2) * Cylinder(cbore_diameter / 2, cbore_depth)

part = solid_body
part.name = "L_Bracket"
export_step(part, "output.step")