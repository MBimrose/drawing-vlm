from build123d import *

leg_length = 80.0
leg_height = 60.0
leg_thickness = 12.0
bracket_depth = 10.0
pocket_width = 6.0
pocket_height = 6.0
pocket_depth = 4.0
hole_diameter = 5.0
hole_spacing = 30.0
hole_count = 2

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0, 0), (leg_length, 0), (leg_length, leg_thickness),
                     (leg_thickness, leg_thickness), (leg_thickness, leg_height),
                     (0, leg_height), close=True)
        make_face()
    extrude(amount=bracket_depth)

solid_body = p.part

pocket = Pos(leg_thickness - pocket_depth/2, leg_height/2, bracket_depth/2) * Box(pocket_depth, pocket_width, pocket_height)
solid_body = solid_body - pocket

for i in range(hole_count):
    y_pos = leg_height/2 + (i - (hole_count-1)/2) * hole_spacing
    hole = Pos(0, y_pos, bracket_depth/2) * Rot(0, 90, 0) * Cylinder(hole_diameter/2, bracket_depth)
    solid_body = solid_body - hole

part = solid_body
part.name = "L_bracket"
export_step(part, "output.step")