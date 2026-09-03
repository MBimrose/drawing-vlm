from build123d import *

leg_a = 60.0
leg_b = 50.0
thickness = 8.0
inner_fillet_radius = 3.0
hole_diameter = 22.0
rib_width = 20.0
rib_height = 15.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0, 0), (leg_a, 0), (leg_a, thickness), (thickness, thickness), (thickness, leg_b), (0, leg_b), close=True)
        make_face()
    extrude(amount=thickness)

solid_body = p.part
solid_body = fillet(solid_body.edges().filter_by(Axis.Z), inner_fillet_radius)

solid_body = solid_body - Pos(thickness, thickness, 0) * Cylinder(hole_diameter / 2, thickness * 2)

with BuildPart() as rib_p:
    with BuildSketch() as rib_sk:
        with BuildLine() as rib_bl:
            Polyline((0, 0), (rib_width, 0), (0, rib_height), close=True)
        make_face()
    extrude(amount=thickness)

rib_body = Pos(thickness, thickness, 0) * rib_p.part
solid_body = solid_body + rib_body

part = solid_body
part.name = "L_bracket_with_rib"
export_step(part, "output.step")