from build123d import *

vertical_leg_length = 70.0
horizontal_leg_length = 80.0
leg_width = 20.0
thickness = 8.0
gusset_length = 30.0
gusset_thickness = 5.0
hole_diameter = 6.0
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

with BuildPart() as g:
    with BuildSketch() as gsk:
        with BuildLine() as gbl:
            Polyline((leg_width, leg_width), (leg_width + gusset_length, leg_width),
                     (leg_width, leg_width + gusset_length), close=True)
        make_face()
    extrude(amount=gusset_thickness)

solid_body = solid_body + g.part

hole_center_x = leg_width / 2
hole_center_y = vertical_leg_length / 2
solid_body = solid_body - Pos(hole_center_x, hole_center_y, 0) * Cylinder(hole_diameter / 2, thickness * 2)

bottom_face = solid_body.faces().sort_by(Axis.Y)[0]
solid_body = chamfer(bottom_face.edges(), chamfer_distance)

part = solid_body
part.name = "L_Bracket"
export_step(part, "output.step")