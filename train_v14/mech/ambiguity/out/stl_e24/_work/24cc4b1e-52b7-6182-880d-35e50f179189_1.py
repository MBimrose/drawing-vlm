from build123d import *

leg_length_long = 80.0
leg_length_short = 50.0
leg_width = 20.0
thickness = 8.0
fillet_radius = 2.0
counterbore_diameter = 10.0
counterbore_depth = 4.0
through_hole_diameter = 6.0
through_hole_offset = 30.0
pattern_hole_diameter = 4.0
pattern_hole_count = 4
pattern_hole_spacing = (leg_length_long - 2 * leg_width) / (pattern_hole_count + 1)

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0, 0), (leg_length_long, 0), (leg_length_long, leg_width),
                     (leg_width, leg_width), (leg_width, leg_length_short + leg_width),
                     (0, leg_length_short + leg_width), close=True)
        make_face()
    extrude(amount=thickness)

solid_body = p.part
solid_body = fillet(solid_body.edges(), fillet_radius)

cbore_cyl = Pos(counterbore_depth/2, leg_width/2 + through_hole_offset, thickness/2) * Rot(0, 90, 0) * Cylinder(counterbore_diameter/2, counterbore_depth)
through_cyl = Pos(thickness/2, leg_width/2 + through_hole_offset, thickness/2) * Rot(0, 90, 0) * Cylinder(through_hole_diameter/2, thickness)
solid_body = solid_body - cbore_cyl - through_cyl

for i in range(pattern_hole_count):
    x = leg_width + pattern_hole_spacing * (i + 1)
    y = leg_width / 2
    hole = Pos(x, y, thickness/2) * Cylinder(pattern_hole_diameter/2, thickness)
    solid_body = solid_body - hole

part = solid_body
part.name = "L_bracket"
export_step(part, "output.step")