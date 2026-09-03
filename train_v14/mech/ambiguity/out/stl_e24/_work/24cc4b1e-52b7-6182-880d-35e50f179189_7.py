from build123d import *

leg_length = 80.0
leg_height = 70.0
leg_width = 20.0
thickness = 8.0
fillet_radius = 2.0
hole_diameter = 4.0
hole_count = 4
hole_margin = 10.0
counterbore_diameter = 6.0
counterbore_depth = 4.0
counterbore_cbore_diameter = 10.0
counterbore_cbore_depth = 2.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            l1 = Line((0, 0), (leg_length, 0))
            l2 = Line(l1 @ 1, (leg_length, leg_width))
            l3 = Line(l2 @ 1, (leg_width, leg_width))
            l4 = Line(l3 @ 1, (leg_width, leg_height))
            l5 = Line(l4 @ 1, (0, leg_height))
            l6 = Line(l5 @ 1, (0, 0))
        make_face()
    extrude(amount=thickness)

solid_body = p.part
solid_body = fillet(solid_body.edges(), fillet_radius)

spacing = (leg_length - 2 * hole_margin) / (hole_count - 1)
for i in range(hole_count):
    x = hole_margin + i * spacing
    y = leg_width / 2
    solid_body = solid_body - Pos(x, y, thickness / 2) * Cylinder(hole_diameter / 2, thickness)

cbore_x = 0
cbore_y = leg_height / 2
cbore_z = thickness / 2
solid_body = solid_body - Pos(cbore_x + counterbore_cbore_depth / 2, cbore_y, cbore_z) * Rot(0, 90, 0) * Cylinder(counterbore_cbore_diameter / 2, counterbore_cbore_depth)
solid_body = solid_body - Pos(cbore_x + counterbore_depth / 2, cbore_y, cbore_z) * Rot(0, 90, 0) * Cylinder(counterbore_diameter / 2, counterbore_depth)

part = solid_body
part.name = "L_Bracket"
export_step(part, "output.step")