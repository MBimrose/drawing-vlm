from build123d import *

leg_length = 80.0
leg_height = 30.0
thickness = 5.0
depth = 10.0
fillet_radius = 2.0

with BuildPart() as p:
    with BuildSketch() as s:
        with BuildLine() as l:
            Polyline((0,0), (leg_length,0), (leg_length,thickness), (thickness,thickness), (thickness,leg_height), (0,leg_height), close=True)
        make_face()
    extrude(amount=depth)
solid_body = p.part
solid_body = fillet(solid_body.edges(), fillet_radius)
part = solid_body
part.name = "L_bracket"
export_step(part, "output.step")