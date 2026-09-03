from build123d import *

leg_long = 80.0
leg_short = 60.0
leg_thickness = 10.0
bracket_thickness = 8.0
gusset_height = 12.0
gusset_thickness = 4.0
hole_diameter = 4.0
hole_spacing = 15.0
hole_offset = 20.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0, 0), (leg_short, 0), (leg_short, leg_thickness),
                     (leg_thickness, leg_thickness), (leg_thickness, leg_long),
                     (0, leg_long), close=True)
        make_face()
    extrude(amount=bracket_thickness)

solid_body = p.part

with BuildPart() as g:
    with BuildSketch() as gsk:
        with BuildLine() as gbl:
            Polyline((0, 0), (gusset_height, 0), (0, gusset_height), close=True)
        make_face()
    extrude(amount=bracket_thickness + gusset_thickness)

solid_body = solid_body + g.part

for i in range(3):
    x = hole_offset + i * hole_spacing
    y = leg_thickness / 2
    solid_body = solid_body - Pos(x, y, bracket_thickness) * Cylinder(hole_diameter / 2, bracket_thickness)

part = solid_body
part.name = "L_Bracket"
export_step(part, "output.step")