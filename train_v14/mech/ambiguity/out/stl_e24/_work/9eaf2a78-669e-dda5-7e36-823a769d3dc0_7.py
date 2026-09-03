from build123d import *

leg_length = 80.0
leg_height = 60.0
leg_thickness = 12.0
bracket_thickness = 8.0
fillet_radius = 1.0
hole_diameter = 6.0
hole_depth = 5.0
hole_spacing = 20.0
hole_offset_from_top = 15.0
rib_width = 6.0
rib_height = 10.0
rib_offset_from_top = 10.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            l1 = Line((0, 0), (leg_length, 0))
            l2 = Line(l1 @ 1, (leg_length, leg_thickness))
            l3 = Line(l2 @ 1, (leg_thickness, leg_thickness))
            l4 = Line(l3 @ 1, (leg_thickness, leg_height + leg_thickness))
            l5 = Line(l4 @ 1, (0, leg_height + leg_thickness))
            l6 = Line(l5 @ 1, (0, 0))
        make_face()
    extrude(amount=bracket_thickness)

solid_body = p.part
solid_body = fillet(solid_body.edges().filter_by(Axis.Z), fillet_radius)

rib = Pos(leg_thickness/2, leg_height - rib_offset_from_top, bracket_thickness/2) * Box(rib_height, rib_width, bracket_thickness)
solid_body = solid_body + rib

for i in range(2):
    y_pos = leg_height - hole_offset_from_top - i * hole_spacing
    hole = Pos(leg_length - hole_depth/2, y_pos, bracket_thickness/2) * Rot(0, 90, 0) * Cylinder(hole_diameter/2, hole_depth)
    solid_body = solid_body - hole

part = solid_body
part.name = "L_Bracket"
export_step(part, "output.step")