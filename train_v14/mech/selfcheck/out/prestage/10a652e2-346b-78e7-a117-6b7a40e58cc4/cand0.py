from build123d import *

leg_length_x = 80.0
leg_length_y = 60.0
thickness = 10.0
depth = 20.0
inner_fillet_radius = 2.0
hole_diameter = 5.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0, 0), (leg_length_x + thickness, 0), (leg_length_x + thickness, thickness),
                     (thickness, thickness), (thickness, leg_length_y + thickness),
                     (0, leg_length_y + thickness), close=True)
        make_face()
    extrude(amount=depth)

solid_body = p.part
solid_body = fillet(solid_body.edges(), inner_fillet_radius)
solid_body = solid_body - Pos(thickness, thickness, depth/2) * Cylinder(hole_diameter/2, depth)

part = solid_body
part.name = "L_bracket"
export_step(part, "output.step")