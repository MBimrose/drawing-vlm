from build123d import *

leg_length = 80.0
leg_height = 60.0
leg_thickness = 12.0
bracket_thickness = 10.0
gusset_width = 20.0
gusset_height = 20.0
hole_diameter = 5.0
hole_offset = 15.0
pocket_width = 6.0
pocket_depth = 4.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0, 0), (leg_length, 0), (leg_length, leg_thickness),
                     (leg_thickness, leg_thickness), (leg_thickness, leg_height),
                     (0, leg_height), close=True)
        make_face()
    extrude(amount=bracket_thickness)

solid_body = p.part

for y_pos in [hole_offset, leg_height - hole_offset]:
    solid_body = solid_body - Pos(0, y_pos, bracket_thickness / 2) * Rot(0, 90, 0) * Cylinder(hole_diameter / 2, bracket_thickness)

solid_body = solid_body - Pos(leg_thickness / 2, leg_height / 2, bracket_thickness / 2) * Box(pocket_depth, pocket_width, pocket_width)

with BuildPart() as gp:
    with BuildSketch() as gsk:
        with BuildLine() as gbl:
            Polyline((0, 0), (gusset_width, 0), (0, gusset_height), close=True)
        make_face()
    extrude(amount=bracket_thickness)

solid_body = solid_body + gp.part

part = solid_body
part.name = "L_Bracket"
export_step(part, "output.step")