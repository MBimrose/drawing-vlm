from build123d import *

leg_length = 80.0
leg_width = 30.0
thickness = 5.0
bracket_depth = 10.0
fillet_radius = 2.0
hole_diameter = 6.0
hole_offset = 20.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0, 0), (leg_length, 0), (leg_length, thickness),
                     (thickness, thickness), (thickness, leg_width),
                     (0, leg_width), close=True)
        make_face()
    extrude(amount=bracket_depth)

solid_body = p.part
solid_body = fillet(solid_body.edges(), fillet_radius)

hole_x = leg_length / 2 + hole_offset
hole_y = thickness / 2
solid_body = solid_body - Pos(hole_x, hole_y, 0) * Cylinder(hole_diameter / 2, bracket_depth * 2)

part = solid_body
part.name = "L_bracket"
export_step(part, "output.step")