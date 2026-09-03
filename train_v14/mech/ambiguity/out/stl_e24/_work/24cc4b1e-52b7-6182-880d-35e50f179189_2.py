from build123d import *

horizontal_leg_length = 80.0
vertical_leg_length = 70.0
leg_width = 20.0
thickness = 8.0
fillet_radius = 2.0
hole_diameter = 4.0
hole_count = 4
hole_offset_from_corner = 15.0
rib_width = 6.0
rib_height = 30.0
rib_thickness = 4.0
counterbore_diameter = 6.0
counterbore_depth = 4.0
counterbore_outer_diameter = 10.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            l1 = Line((0, 0), (horizontal_leg_length, 0))
            l2 = Line(l1 @ 1, (horizontal_leg_length, leg_width))
            l3 = Line(l2 @ 1, (leg_width, leg_width))
            l4 = Line(l3 @ 1, (leg_width, vertical_leg_length))
            l5 = Line(l4 @ 1, (0, vertical_leg_length))
            l6 = Line(l5 @ 1, (0, 0))
        make_face()
    extrude(amount=thickness)

solid_body = p.part
solid_body = fillet(solid_body.edges(), fillet_radius)

hole_spacing = (horizontal_leg_length - 2 * hole_offset_from_corner) / (hole_count - 1)
for i in range(hole_count):
    x = hole_offset_from_corner + i * hole_spacing
    y = leg_width / 2
    solid_body = solid_body - Pos(x, y, 0) * Cylinder(hole_diameter / 2, thickness * 2)

cbore_y = vertical_leg_length / 2
cbore_z = thickness / 2
solid_body = solid_body - Pos(0, cbore_y, cbore_z) * Rot(0, 90, 0) * Cylinder(counterbore_diameter / 2, thickness * 2)
solid_body = solid_body - Pos(0, cbore_y, cbore_z) * Rot(0, 90, 0) * Cylinder(counterbore_outer_diameter / 2, counterbore_depth)

rib = Pos(leg_width / 2, vertical_leg_length / 2, thickness / 2) * Box(rib_width, rib_height, rib_thickness)
solid_body = solid_body + rib

part = solid_body
part.name = "L_Bracket"
export_step(part, "output.step")