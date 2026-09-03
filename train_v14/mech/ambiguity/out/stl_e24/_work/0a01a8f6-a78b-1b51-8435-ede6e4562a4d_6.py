from build123d import *

long_leg = 80.0
short_leg = 30.0
thickness = 5.0
bracket_depth = 10.0
fillet_radius = 2.0
hole_diameter = 4.0
hole_spacing = 15.0
hole_offset = 10.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0,0), (long_leg, 0), (long_leg, thickness), (thickness, thickness), (thickness, short_leg), (0, short_leg), close=True)
        make_face()
    extrude(amount=bracket_depth)

solid_body = p.part
solid_body = fillet(solid_body.edges(), fillet_radius)

for i in range(3):
    y = hole_offset + i * hole_spacing
    solid_body = solid_body - Pos(long_leg, y, bracket_depth/2) * Cylinder(hole_diameter/2, bracket_depth + 1)

part = solid_body
part.name = "L_bracket"
export_step(part, "output.step")