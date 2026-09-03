from build123d import *

leg_length_long = 80.0
leg_length_short = 60.0
leg_thickness = 12.0
bracket_depth = 10.0
pocket_width = 6.0
pocket_height = 6.0
pocket_depth = 4.0
hole_diameter = 5.0
hole_spacing = 30.0
hole_offset_from_bottom = 15.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0, 0), (leg_length_long, 0), (leg_length_long, leg_thickness),
                     (leg_thickness, leg_thickness), (leg_thickness, leg_length_short),
                     (0, leg_length_short), close=True)
        make_face()
    extrude(amount=bracket_depth)

solid_body = p.part

pocket = Pos(leg_thickness - pocket_depth/2, leg_length_short/2, bracket_depth/2) * Box(pocket_depth, pocket_width, pocket_height)
solid_body = solid_body - pocket

for y_pos in [hole_offset_from_bottom, hole_offset_from_bottom + hole_spacing]:
    hole = Pos(0, y_pos, bracket_depth/2) * Rot(0, 90, 0) * Cylinder(hole_diameter/2, bracket_depth)
    solid_body = solid_body - hole

part = solid_body
part.name = "L_bracket"
export_step(part, "output.step")