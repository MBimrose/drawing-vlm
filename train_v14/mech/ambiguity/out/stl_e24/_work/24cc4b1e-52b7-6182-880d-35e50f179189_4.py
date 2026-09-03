from build123d import *

horizontal_leg_length = 80.0
vertical_leg_length = 70.0
leg_width = 20.0
thickness = 8.0
fillet_radius = 2.0
counterbore_diameter = 10.0
counterbore_depth = 4.0
through_hole_diameter = 6.0
through_hole_offset_y = 35.0
through_hole_offset_z = 4.0
small_hole_diameter = 4.0
small_hole_count = 4
small_hole_spacing = (horizontal_leg_length - 2 * leg_width) / (small_hole_count + 1)

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0, 0), (horizontal_leg_length, 0), (horizontal_leg_length, leg_width),
                     (leg_width, leg_width), (leg_width, vertical_leg_length),
                     (0, vertical_leg_length), close=True)
        make_face()
    extrude(amount=thickness)

solid_body = p.part
solid_body = fillet(solid_body.edges(), fillet_radius)

cbore = Pos(counterbore_depth/2, through_hole_offset_y, through_hole_offset_z) * Rot(0, 90, 0) * Cylinder(counterbore_diameter/2, counterbore_depth)
thru = Pos(thickness/2, through_hole_offset_y, through_hole_offset_z) * Rot(0, 90, 0) * Cylinder(through_hole_diameter/2, thickness)
solid_body = solid_body - cbore - thru

for i in range(small_hole_count):
    x = leg_width + small_hole_spacing * (i + 1)
    y = leg_width / 2
    hole = Pos(x, y, thickness/2) * Cylinder(small_hole_diameter/2, thickness)
    solid_body = solid_body - hole

part = solid_body
part.name = "L_Bracket"
export_step(part, "output.step")