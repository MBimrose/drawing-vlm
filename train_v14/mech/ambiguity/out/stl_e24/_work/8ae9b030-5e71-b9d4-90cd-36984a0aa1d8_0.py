from build123d import *

horizontal_leg_length = 80.0
vertical_leg_length = 60.0
leg_thickness = 8.0
bracket_width = 10.0
pocket_width = 30.0
pocket_depth = 6.0
pocket_offset_from_bottom = 5.0
hole_diameter = 6.0
hole_spacing = 20.0
hole_offset_from_edge = 4.0
chamfer_size = 1.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0, 0), (horizontal_leg_length, 0), (horizontal_leg_length, leg_thickness),
                     (leg_thickness, leg_thickness), (leg_thickness, vertical_leg_length),
                     (0, vertical_leg_length), close=True)
        make_face()
    extrude(amount=bracket_width)

solid_body = p.part

pocket = Pos(leg_thickness/2, pocket_offset_from_bottom + pocket_width/2, bracket_width/2) * Box(leg_thickness, pocket_width, pocket_depth)
solid_body = solid_body - pocket

for i in range(3):
    hx = hole_offset_from_edge + i * hole_spacing
    hz = bracket_width / 2
    hole = Pos(hx, leg_thickness/2, hz) * Rot(90, 0, 0) * Cylinder(hole_diameter/2, leg_thickness)
    solid_body = solid_body - hole

part = solid_body
part.name = "L_Bracket"
export_step(part, "output.step")