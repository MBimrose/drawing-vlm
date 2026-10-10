from build123d import *

leg_length_long = 80.0
leg_length_short = 30.0
leg_width = 30.0
leg_thickness = 10.0
bracket_depth = 15.0
wall_thickness = 4.0
shaft_hole_diameter = 12.0
shaft_hole_counterbore_diameter = 20.0
shaft_hole_counterbore_depth = 4.0
mount_hole_diameter = 6.0
mount_hole_counterbore_diameter = 10.0
mount_hole_counterbore_depth = 3.0
mount_hole_spacing = 20.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0, 0), (leg_width + leg_thickness, 0), (leg_width + leg_thickness, leg_length_short),
                     (leg_width, leg_length_short), (leg_width, leg_length_long), (0, leg_length_long), close=True)
        make_face()
    extrude(amount=bracket_depth)

solid_body = p.part
top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face])

solid_body = solid_body - Pos(leg_width/2, leg_length_long, bracket_depth/2) * Cylinder(shaft_hole_diameter/2, bracket_depth)
solid_body = solid_body - Pos(leg_width/2, leg_length_long, bracket_depth - shaft_hole_counterbore_depth/2) * Cylinder(shaft_hole_counterbore_diameter/2, shaft_hole_counterbore_depth)

for x_off in [-mount_hole_spacing/2, mount_hole_spacing/2]:
    solid_body = solid_body - Pos(leg_width/2 + x_off, leg_length_long, bracket_depth/2) * Cylinder(mount_hole_diameter/2, bracket_depth)
    solid_body = solid_body - Pos(leg_width/2 + x_off, leg_length_long, bracket_depth - mount_hole_counterbore_depth/2) * Cylinder(mount_hole_counterbore_diameter/2, mount_hole_counterbore_depth)

part = solid_body
part.name = "L_bracket"
export_step(part, "output.step")