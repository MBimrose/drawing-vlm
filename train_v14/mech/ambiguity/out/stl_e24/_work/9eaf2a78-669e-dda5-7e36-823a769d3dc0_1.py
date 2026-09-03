from build123d import *

long_leg_length = 80.0
short_leg_length = 50.0
leg_width = 12.0
thickness = 8.0
slot_width = 6.0
slot_length = 10.0
slot_offset_from_end = 15.0
hole_diameter = 6.0
hole_depth = 5.0
hole_spacing = 10.0
fillet_radius = 1.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0, 0), (long_leg_length, 0), (long_leg_length, leg_width),
                     (leg_width, leg_width), (leg_width, short_leg_length + leg_width),
                     (0, short_leg_length + leg_width), close=True)
        make_face()
    extrude(amount=thickness)

solid_body = p.part
solid_body = fillet(solid_body.edges().filter_by(Axis.Z), fillet_radius)

slot_center_y = short_leg_length - slot_offset_from_end - slot_length / 2
slot = Pos(leg_width / 2, slot_center_y, thickness / 2) * Box(slot_length, slot_width, thickness)
solid_body = solid_body - slot

hole1 = Pos(long_leg_length - hole_depth / 2, leg_width / 2 - hole_spacing / 2, thickness / 2) * Rot(0, 90, 0) * Cylinder(hole_diameter / 2, hole_depth)
hole2 = Pos(long_leg_length - hole_depth / 2, leg_width / 2 + hole_spacing / 2, thickness / 2) * Rot(0, 90, 0) * Cylinder(hole_diameter / 2, hole_depth)
solid_body = solid_body - hole1 - hole2

part = solid_body
part.name = "L_Bracket"
export_step(part, "output.step")