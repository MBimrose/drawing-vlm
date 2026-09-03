from build123d import *

leg_length = 80.0
leg_width = 15.0
thickness = 8.0
flange_length = 30.0
hole_diameter = 12.0
chamfer_size = 1.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0, 0), (leg_length, 0), (leg_length, leg_width),
                     (leg_length + flange_length, leg_width),
                     (leg_length + flange_length, 0), (0, 0), close=True)
        make_face()
    extrude(amount=thickness)

solid_body = p.part
solid_body = solid_body - Pos(leg_length + flange_length, leg_width, thickness) * Cylinder(hole_diameter / 2, thickness * 2)
solid_body = chamfer(solid_body.edges(), chamfer_size)

part = solid_body
part.name = "L_bracket"
export_step(part, "output.step")