from build123d import *

leg_length = 80.0
leg_height = 70.0
thickness = 6.0
gusset_width = 12.0
gusset_height = 40.0
hole_diameter = 5.0
cbore_diameter = 7.5
cbore_depth = 2.0
hole_spacing = 20.0
hole_offset = 15.0
fillet_radius = 2.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0, 0), (leg_length, 0), (leg_length, thickness), (thickness, thickness), (thickness, leg_height), (0, leg_height), close=True)
        make_face()
    extrude(amount=thickness)

with BuildPart() as g:
    with BuildSketch(Plane.YZ) as gsk:
        with BuildLine() as gbl:
            Polyline((0, 0), (gusset_width, 0), (0, gusset_height), close=True)
        make_face()
    extrude(amount=thickness)

solid_body = p.part + g.part

hole_positions = [
    (hole_offset + i * hole_spacing, thickness / 2) for i in range(3)
] + [
    (thickness / 2, hole_offset + i * hole_spacing) for i in range(3)
]

for x, y in hole_positions:
    solid_body = solid_body - Pos(x, y, thickness - cbore_depth / 2) * Cylinder(cbore_diameter / 2, cbore_depth)
    solid_body = solid_body - Pos(x, y, thickness / 2) * Cylinder(hole_diameter / 2, thickness + 10)

solid_body = fillet(solid_body.edges().filter_by(Axis.Z), fillet_radius)

part = solid_body
part.name = "L_Bracket"
export_step(part, "output.step")