from build123d import *

leg_length = 70.0
leg_width = 30.0
thickness = 8.0
chamfer_size = 3.0
hole_diameter = 6.0
cbore_diameter = 10.0
cbore_depth = 3.0
hole_spacing = 40.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0, 0), (leg_width, 0), (leg_width, leg_length),
                     (leg_width + leg_length, leg_length),
                     (leg_width + leg_length, leg_length + leg_width),
                     (0, leg_length + leg_width), close=True)
        make_face()
    extrude(amount=thickness)

solid_body = p.part

inner_edges = [e for e in solid_body.edges() if abs(e.center().X - leg_width) < 0.1 and abs(e.center().Y - leg_length) < 0.1]
solid_body = chamfer(inner_edges, chamfer_size)

hole_positions = [
    (leg_width / 2, leg_length / 2 - hole_spacing / 2),
    (leg_width / 2, leg_length / 2 + hole_spacing / 2)
]

for x, y in hole_positions:
    solid_body = solid_body - Pos(x, y, thickness / 2) * Cylinder(hole_diameter / 2, thickness)
    solid_body = solid_body - Pos(x, y, thickness - cbore_depth / 2) * Cylinder(cbore_diameter / 2, cbore_depth)

part = solid_body
part.name = "L_Bracket"
export_step(part, "output.step")