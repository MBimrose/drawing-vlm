from build123d import *

horizontal_leg_length = 80.0
vertical_leg_length = 70.0
leg_width = 20.0
thickness = 8.0
fillet_radius = 2.0
counterbore_diameter = 6.0
counterbore_depth = 4.0
counterbore_cbore_diameter = 10.0
counterbore_cbore_depth = 2.0
through_hole_diameter = 4.0
through_hole_count = 4
through_hole_offset = 20.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0,0), (horizontal_leg_length,0), (horizontal_leg_length,leg_width),
                     (leg_width,leg_width), (leg_width,vertical_leg_length), (0,vertical_leg_length), close=True)
        make_face()
    extrude(amount=thickness)

solid_body = p.part
solid_body = fillet(solid_body.edges(), fillet_radius)

cbore_y = vertical_leg_length / 2
cbore_z = thickness / 2
solid_body = solid_body - Pos(0, cbore_y, cbore_z) * Rot(0, 90, 0) * Cylinder(counterbore_diameter/2, thickness)
solid_body = solid_body - Pos(0, cbore_y, cbore_z) * Rot(0, 90, 0) * Cylinder(counterbore_cbore_diameter/2, counterbore_cbore_depth)

spacing = (horizontal_leg_length - 2 * through_hole_offset) / (through_hole_count - 1)
for i in range(through_hole_count):
    hx = through_hole_offset + i * spacing
    hy = leg_width / 2
    solid_body = solid_body - Pos(hx, hy, thickness/2) * Cylinder(through_hole_diameter/2, thickness)

part = solid_body
part.name = "L_Bracket"
export_step(part, "output.step")