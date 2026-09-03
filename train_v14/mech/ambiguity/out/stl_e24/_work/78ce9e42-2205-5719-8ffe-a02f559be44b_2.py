from build123d import *

leg_length_x = 60.0
leg_length_y = 50.0
leg_width = 15.0
thickness = 8.0
pocket_diameter = 22.0
pocket_offset_x = 20.0
pocket_offset_y = 20.0
fillet_radius = 3.0
notch_width = 10.0
notch_height = 20.0
notch_depth = 6.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0, 0), (leg_length_x, 0), (leg_length_x, leg_width),
                     (leg_width, leg_width), (leg_width, leg_length_y),
                     (0, leg_length_y), close=True)
        make_face()
    extrude(amount=thickness)

solid_body = p.part
solid_body = fillet(solid_body.edges().filter_by(Axis.Z), fillet_radius)

notch = Pos(leg_width - notch_depth/2, leg_length_y/2, thickness/2) * Box(notch_depth, notch_height, notch_width)
solid_body = solid_body - notch

pocket = Pos(pocket_offset_x, pocket_offset_y, thickness/2) * Cylinder(pocket_diameter/2, thickness)
solid_body = solid_body - pocket

part = solid_body
part.name = "L_bracket"
export_step(part, "output.step")