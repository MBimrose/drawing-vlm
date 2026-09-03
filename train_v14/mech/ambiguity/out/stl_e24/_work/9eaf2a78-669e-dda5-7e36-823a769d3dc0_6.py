from build123d import *

horizontal_leg_length = 80.0
vertical_leg_length = 65.0
leg_width = 12.0
bracket_thickness = 8.0
slot_width = 10.0
slot_height = 6.0
slot_offset_from_top = 15.0
fillet_radius = 1.0
hole_diameter = 6.0
hole_depth = 5.0
hole_spacing = 10.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0, 0), (horizontal_leg_length, 0), (horizontal_leg_length, leg_width),
                     (leg_width, leg_width), (leg_width, vertical_leg_length), (0, vertical_leg_length), close=True)
        make_face()
    extrude(amount=bracket_thickness)

solid = p.part
solid = fillet(solid.edges().filter_by(Axis.Z), fillet_radius)

slot_center_y = vertical_leg_length - slot_offset_from_top - slot_height / 2
slot = Pos(leg_width / 2, slot_center_y, bracket_thickness / 2) * Box(slot_width, slot_height, bracket_thickness)
solid = solid - slot

hole_r = hole_diameter / 2
for y in [leg_width / 2 - hole_spacing / 2, leg_width / 2 + hole_spacing / 2]:
    hole = Pos(horizontal_leg_length - hole_depth / 2, y, bracket_thickness / 2) * Rot(0, 90, 0) * Cylinder(hole_r, hole_depth)
    solid = solid - hole

part = solid
part.name = "L_Bracket"
export_step(part, "output.step")