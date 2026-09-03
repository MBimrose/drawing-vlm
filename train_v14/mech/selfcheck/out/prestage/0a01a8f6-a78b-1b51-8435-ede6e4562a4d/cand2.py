from build123d import *

leg_length_long = 80.0
leg_length_short = 30.0
thickness = 5.0
extrude_depth = 10.0
fillet_radius = 2.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0,0), (leg_length_long,0), (leg_length_long,thickness), (thickness,thickness), (thickness,leg_length_short), (0,leg_length_short), close=True)
        make_face()
    extrude(amount=extrude_depth)

solid_body = p.part
solid_body = fillet(solid_body.edges(), fillet_radius)
part = solid_body
part.name = "L_bracket"
export_step(part, "output.step")