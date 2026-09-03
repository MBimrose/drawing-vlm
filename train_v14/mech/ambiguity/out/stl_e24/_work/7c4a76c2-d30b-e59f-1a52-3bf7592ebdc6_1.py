from build123d import *

leg_length = 70.0
leg_height = 60.0
leg_width = 30.0
thickness = 8.0
gusset_thickness = 8.0
hole_diameter = 6.0
cbore_diameter = 10.0
cbore_depth = 3.0
hole_offset = 15.0
fillet_radius = 2.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0, 0), (leg_width, 0), (leg_width, leg_height),
                     (leg_width + leg_length, leg_height),
                     (leg_width + leg_length, leg_height + leg_width),
                     (0, leg_height + leg_width), close=True)
        make_face()
    extrude(amount=thickness)

with BuildPart() as g:
    with BuildSketch() as gsk:
        with BuildLine() as gbl:
            Polyline((leg_width, leg_height), (leg_width + gusset_thickness, leg_height),
                     (leg_width, leg_height + gusset_thickness), close=True)
        make_face()
    extrude(amount=thickness)

solid_body = p.part + g.part

hole_positions = [
    (leg_width / 2, hole_offset),
    (leg_width / 2, leg_height - hole_offset)
]

for x, y in hole_positions:
    solid_body = solid_body - Pos(x, y, thickness / 2) * Cylinder(hole_diameter / 2, thickness)
    solid_body = solid_body - Pos(x, y, thickness - cbore_depth / 2) * Cylinder(cbore_diameter / 2, cbore_depth)

inner_edges = [e for e in solid_body.edges() if abs(e.center().X - leg_width) < 1e-3 and abs(e.center().Y - leg_height) < 1e-3]
solid_body = fillet(inner_edges, fillet_radius)

part = solid_body
part.name = "L_Bracket"
export_step(part, "output.step")