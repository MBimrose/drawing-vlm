from build123d import *

leg_length_long = 60.0
leg_length_short = 50.0
leg_width = 15.0
thickness = 8.0
inner_fillet_radius = 3.0
cutout_radius = 12.0
pocket_width = 10.0
pocket_depth = 20.0
pocket_height = 6.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0, 0), (leg_length_long, 0), (leg_length_long, leg_width),
                     (leg_width, leg_width), (leg_width, leg_length_short),
                     (0, leg_length_short), close=True)
        make_face()
    extrude(amount=thickness)

solid_body = p.part
solid_body = fillet(solid_body.edges().filter_by(Axis.Z), inner_fillet_radius)
solid_body = solid_body - Pos(leg_width, leg_width, thickness/2) * Cylinder(cutout_radius, thickness)
solid_body = solid_body - Pos(leg_width/2, leg_length_short - pocket_height/2, thickness/2) * Box(pocket_width, pocket_height, pocket_depth)

part = solid_body
part.name = "L_bracket"
export_step(part, "output.step")