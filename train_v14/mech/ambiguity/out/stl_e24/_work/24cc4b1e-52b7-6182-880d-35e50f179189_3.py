from build123d import *

leg_length_long = 80.0
leg_length_short = 50.0
leg_width = 20.0
thickness = 8.0
fillet_radius = 2.0
counterbore_diameter = 6.0
counterbore_depth = 4.0
through_hole_diameter = 10.0
through_hole_depth = 5.0
rib_thickness = 3.0
rib_height = 12.0
rib_offset = 5.0
mount_hole_diameter = 4.0
mount_hole_count = 4
mount_hole_spacing = (leg_length_long - 2 * leg_width) / (mount_hole_count + 1)

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            l1 = Line((0, 0), (leg_length_long, 0))
            l2 = Line(l1 @ 1, (leg_length_long, leg_width))
            l3 = Line(l2 @ 1, (leg_width, leg_width))
            l4 = Line(l3 @ 1, (leg_width, leg_length_short + leg_width))
            l5 = Line(l4 @ 1, (0, leg_length_short + leg_width))
            l6 = Line(l5 @ 1, (0, 0))
        make_face()
    extrude(amount=thickness)

solid_body = p.part
solid_body = fillet(solid_body.edges(), fillet_radius)

cbore_cyl = Pos(0, leg_length_short / 2 + leg_width, thickness / 2) * Rot(0, 90, 0) * Cylinder(counterbore_diameter / 2, counterbore_depth)
solid_body = solid_body - cbore_cyl

thru_cyl = Pos(0, leg_length_short / 2 + leg_width, thickness / 2) * Rot(0, 90, 0) * Cylinder(through_hole_diameter / 2, through_hole_depth)
solid_body = solid_body - thru_cyl

rib = Pos(leg_width / 2, leg_width / 2, thickness / 2) * Box(rib_thickness, rib_height, thickness)
solid_body = solid_body + rib

for i in range(mount_hole_count):
    x = leg_width + mount_hole_spacing * (i + 1)
    y = leg_width / 2
    hole = Pos(x, y, thickness / 2) * Cylinder(mount_hole_diameter / 2, thickness)
    solid_body = solid_body - hole

part = solid_body
part.name = "L_bracket"
export_step(part, "output.step")