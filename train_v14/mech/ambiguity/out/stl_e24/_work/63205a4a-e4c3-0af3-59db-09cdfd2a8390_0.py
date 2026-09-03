from build123d import *

vertical_leg_length = 70.0
horizontal_leg_length = 80.0
leg_width = 20.0
thickness = 8.0
rib_thickness = 5.0
rib_length = 30.0
hole_diameter = 6.0
hole_offset_from_bottom = 20.0
chamfer_distance = 1.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0, 0), (0, vertical_leg_length), (leg_width, vertical_leg_length),
                     (leg_width, leg_width), (horizontal_leg_length, leg_width),
                     (horizontal_leg_length, 0), close=True)
        make_face()
    extrude(amount=thickness)

solid_body = p.part

with BuildPart() as rib_p:
    with BuildSketch() as rib_sk:
        with BuildLine() as rib_bl:
            Polyline((leg_width, leg_width), (leg_width + rib_length, leg_width),
                     (leg_width, leg_width + rib_length), close=True)
        make_face()
    extrude(amount=rib_thickness)

solid_body = solid_body + rib_p.part

hole_center_x = leg_width / 2
hole_center_y = hole_offset_from_bottom
solid_body = solid_body - Pos(hole_center_x, hole_center_y, 0) * Cylinder(hole_diameter / 2, thickness + 10)

bottom_face = solid_body.faces().sort_by(Axis.Y)[0]
solid_body = chamfer(bottom_face.edges(), chamfer_distance)

left_face = solid_body.faces().sort_by(Axis.X)[0]
solid_body = chamfer(left_face.edges(), chamfer_distance)

part = solid_body
part.name = "L_Bracket"
export_step(part, "output.step")