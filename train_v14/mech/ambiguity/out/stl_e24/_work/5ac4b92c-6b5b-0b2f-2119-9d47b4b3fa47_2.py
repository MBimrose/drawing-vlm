from build123d import *

leg_length_long = 80.0
leg_length_short = 60.0
bracket_thickness = 10.0
bracket_height = 12.0
fillet_radius = 2.0
pocket_width = 30.0
pocket_depth = 6.0
pocket_height = 4.0
blind_hole_diameter = 4.5
blind_hole_depth = 8.0
mount_hole_diameter = 6.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            l1 = Line((0, 0), (leg_length_long, 0))
            l2 = Line(l1 @ 1, (leg_length_long, bracket_thickness))
            l3 = Line(l2 @ 1, (bracket_thickness, bracket_thickness))
            l4 = Line(l3 @ 1, (bracket_thickness, leg_length_short + bracket_thickness))
            l5 = Line(l4 @ 1, (0, leg_length_short + bracket_thickness))
            l6 = Line(l5 @ 1, (0, 0))
        make_face()
    extrude(amount=bracket_height)

solid_body = p.part
solid_body = fillet(solid_body.edges().filter_by(Axis.Z), fillet_radius)

pocket = Pos(bracket_thickness/2, leg_length_short + bracket_thickness - pocket_depth/2, bracket_height - pocket_height/2) * Box(pocket_width, pocket_depth, pocket_height)
solid_body = solid_body - pocket

blind_hole = Pos(bracket_thickness/2, leg_length_short + bracket_thickness - pocket_depth/2, bracket_height - blind_hole_depth/2) * Cylinder(blind_hole_diameter/2, blind_hole_depth)
solid_body = solid_body - blind_hole

mount_hole1 = Pos(leg_length_long/2, bracket_thickness/2, 0) * Cylinder(mount_hole_diameter/2, bracket_height + 1)
solid_body = solid_body - mount_hole1

mount_hole2 = Pos(bracket_thickness/2, leg_length_short/2 + bracket_thickness, 0) * Cylinder(mount_hole_diameter/2, bracket_height + 1)
solid_body = solid_body - mount_hole2

part = solid_body
part.name = "L_bracket"
export_step(part, "output.step")