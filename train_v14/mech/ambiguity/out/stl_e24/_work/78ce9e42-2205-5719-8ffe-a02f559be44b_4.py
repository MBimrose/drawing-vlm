from build123d import *

horizontal_leg_length = 60.0
vertical_leg_length = 50.0
leg_thickness = 8.0
bracket_thickness = 8.0
inner_fillet_radius = 3.0
notch_width = 12.0
notch_height = 10.0
notch_offset = 5.0
hole_diameter = 22.0
hole_center_x = 20.0
hole_center_y = 15.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0, 0), (horizontal_leg_length, 0), (horizontal_leg_length, leg_thickness),
                     (leg_thickness, leg_thickness), (leg_thickness, vertical_leg_length),
                     (0, vertical_leg_length), close=True)
        make_face()
    extrude(amount=bracket_thickness)

solid_body = p.part
solid_body = fillet(solid_body.edges().filter_by(Axis.Z), inner_fillet_radius)

notch = Pos(leg_thickness + notch_offset, vertical_leg_length - notch_height - notch_offset, bracket_thickness/2) * Box(notch_width, notch_height, bracket_thickness)
solid_body = solid_body - notch

hole = Pos(hole_center_x, hole_center_y, bracket_thickness/2) * Cylinder(hole_diameter/2, bracket_thickness)
solid_body = solid_body - hole

part = solid_body
part.name = "L_Bracket"
export_step(part, "output.step")