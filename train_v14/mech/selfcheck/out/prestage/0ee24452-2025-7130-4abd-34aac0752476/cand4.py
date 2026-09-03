from build123d import *

vertical_leg_length = 70.0
horizontal_leg_length = 60.0
leg_thickness = 8.0
bracket_depth = 20.0
gusset_thickness = 4.0
hole_diameter = 5.0
hole_spacing = 20.0
hole_offset_from_edge = 10.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0, 0), (0, vertical_leg_length), (leg_thickness, vertical_leg_length),
                     (leg_thickness, leg_thickness), (horizontal_leg_length, leg_thickness),
                     (horizontal_leg_length, 0), close=True)
        make_face()
    extrude(amount=bracket_depth)

solid_body = p.part

with BuildPart() as g:
    with BuildSketch() as gsk:
        with BuildLine() as gbl:
            Polyline((leg_thickness, vertical_leg_length),
                     (leg_thickness + gusset_thickness, vertical_leg_length),
                     (leg_thickness, vertical_leg_length - gusset_thickness), close=True)
        make_face()
    extrude(amount=bracket_depth)

solid_body = solid_body + g.part

for i in range(3):
    x = hole_offset_from_edge + i * hole_spacing
    solid_body = solid_body - Pos(x, 0, bracket_depth / 2) * Rot(90, 0, 0) * Cylinder(hole_diameter / 2, vertical_leg_length + 10)

part = solid_body
part.name = "L_Bracket"
export_step(part, "output.step")