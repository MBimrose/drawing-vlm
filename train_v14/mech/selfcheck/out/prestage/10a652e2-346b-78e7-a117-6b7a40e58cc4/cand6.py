from build123d import *

leg_length = 80.0
leg_height = 60.0
thickness = 10.0
width = 20.0
fillet_radius = 2.0
hole_diameter = 5.0
hole_offset = 5.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0, 0), (leg_length + thickness, 0), (leg_length + thickness, thickness),
                     (thickness, thickness), (thickness, leg_height + thickness),
                     (0, leg_height + thickness), close=True)
        make_face()
    extrude(amount=width)

solid_body = p.part
solid_body = fillet(solid_body.edges(), fillet_radius)
solid_body = solid_body - Pos(hole_offset, hole_offset, width/2) * Cylinder(hole_diameter/2, width + 2)

part = solid_body
part.name = "L_bracket"
export_step(part, "output.step")