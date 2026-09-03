from build123d import *

leg_length_x = 80.0
leg_length_y = 70.0
thickness = 10.0
rib_thickness = 6.0
pocket_width = 20.0
pocket_length = 30.0
pocket_depth = 5.0
counterbore_diameter = 8.0
counterbore_depth = 4.0
through_hole_diameter = 4.0
mount_hole_diameter = 5.0
mount_hole_spacing = 40.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            l1 = Line((0, 0), (leg_length_x, 0))
            l2 = Line(l1 @ 1, (leg_length_x, thickness))
            l3 = Line(l2 @ 1, (thickness, thickness))
            l4 = Line(l3 @ 1, (thickness, leg_length_y))
            l5 = Line(l4 @ 1, (0, leg_length_y))
            l6 = Line(l5 @ 1, (0, 0))
        make_face()
    extrude(amount=thickness)

solid_body = p.part

with BuildPart() as rib_p:
    with BuildSketch() as rib_sk:
        with BuildLine() as rib_bl:
            rl1 = Line((0, 0), (thickness, 0))
            rl2 = Line(rl1 @ 1, (0, thickness))
            rl3 = Line(rl2 @ 1, (0, 0))
        make_face()
    extrude(amount=thickness)

solid_body = solid_body + rib_p.part

pocket = Pos(leg_length_x - pocket_length/2, thickness/2, thickness - pocket_depth/2) * Box(pocket_width, pocket_length, pocket_depth)
solid_body = solid_body - pocket

cbore = Pos(thickness/2, leg_length_y/2, thickness - counterbore_depth/2) * Cylinder(counterbore_diameter/2, counterbore_depth)
solid_body = solid_body - cbore

thru = Pos(thickness/2, leg_length_y/2, thickness/2) * Cylinder(through_hole_diameter/2, thickness)
solid_body = solid_body - thru

for dx in [-mount_hole_spacing/2, mount_hole_spacing/2]:
    mh = Pos(leg_length_x/2 + dx, 0, thickness/2) * Cylinder(mount_hole_diameter/2, thickness)
    solid_body = solid_body - mh

part = solid_body
part.name = "L_bracket"
export_step(part, "output.step")