from build123d import *

leg_length = 80.0
leg_height = 70.0
thickness = 6.0
gusset_height = 48.0
gusset_thickness = 6.0
hole_diameter = 5.0
cbore_diameter = 7.5
cbore_depth = 2.0
fillet_radius = 2.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0, 0), (leg_length, 0), (leg_length, thickness), (thickness, thickness), (thickness, leg_height), (0, leg_height), close=True)
        make_face()
    extrude(amount=thickness)

solid_body = p.part

with BuildPart() as g:
    with BuildSketch(Plane.YZ) as gsk:
        with BuildLine() as gbl:
            Polyline((0, 0), (gusset_thickness, 0), (0, gusset_height), close=True)
        make_face()
    extrude(amount=thickness)

gusset_body = Pos(0, thickness, 0) * g.part
solid_body = solid_body + gusset_body

hole_positions = [
    (leg_length * 0.25, thickness / 2),
    (leg_length * 0.5, thickness / 2),
    (leg_length * 0.75, thickness / 2),
    (thickness / 2, leg_height * 0.33),
    (thickness / 2, leg_height * 0.66),
]

for x, y in hole_positions:
    solid_body = solid_body - Pos(x, y, thickness - cbore_depth / 2) * Cylinder(cbore_diameter / 2, cbore_depth)
    solid_body = solid_body - Pos(x, y, thickness / 2) * Cylinder(hole_diameter / 2, thickness + 10)

vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = fillet(vertical_edges, fillet_radius)

part = solid_body
part.name = "L_Bracket"
export_step(part, "output.step")