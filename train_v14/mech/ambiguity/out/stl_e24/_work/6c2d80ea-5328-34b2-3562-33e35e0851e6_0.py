from build123d import *

vertical_leg_length = 80.0
horizontal_leg_length = 60.0
leg_thickness = 10.0
bracket_depth = 8.0
gusset_width = 12.0
gusset_height = 12.0
gusset_thickness = 4.0
hole_diameter = 4.0
hole_spacing = 15.0
hole_count = 3
hole_offset_from_corner = 20.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0, 0), (0, vertical_leg_length), (leg_thickness, vertical_leg_length),
                     (leg_thickness, leg_thickness), (horizontal_leg_length, leg_thickness),
                     (horizontal_leg_length, 0), close=True)
        make_face()
    extrude(amount=bracket_depth)

with BuildPart() as g:
    with BuildSketch() as gsk:
        with BuildLine() as gbl:
            Polyline((0, 0), (gusset_width, 0), (0, gusset_height), close=True)
        make_face()
    extrude(amount=bracket_depth + gusset_thickness)

solid_body = p.part + g.part

for i in range(hole_count):
    x = hole_offset_from_corner + i * hole_spacing
    y = leg_thickness / 2
    solid_body = solid_body - Pos(x, y, bracket_depth) * Cylinder(hole_diameter / 2, bracket_depth)

part = solid_body
part.name = "L_Bracket"
export_step(part, "output.step")