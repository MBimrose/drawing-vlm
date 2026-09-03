from build123d import *

horizontal_leg_length = 60.0
vertical_leg_length = 50.0
leg_thickness = 8.0
bracket_thickness = 8.0
inner_fillet_radius = 3.0
hole_diameter = 22.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0, 0), (horizontal_leg_length, 0), (horizontal_leg_length, leg_thickness),
                     (leg_thickness, leg_thickness), (leg_thickness, vertical_leg_length),
                     (0, vertical_leg_length), close=True)
        make_face()
    extrude(amount=bracket_thickness)

solid_body = p.part
solid_body = fillet(solid_body.edges().filter_by(Axis.Z), inner_fillet_radius)
solid_body = solid_body - Pos(leg_thickness, leg_thickness, 0) * Cylinder(hole_diameter / 2, bracket_thickness * 2)

part = solid_body
part.name = "L_Bracket"
export_step(part, "output.step")