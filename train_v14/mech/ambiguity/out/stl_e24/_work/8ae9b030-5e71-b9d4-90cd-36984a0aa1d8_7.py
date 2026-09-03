from build123d import *

horizontal_leg_length = 80.0
vertical_leg_length = 60.0
leg_thickness = 8.0
bracket_thickness = 10.0
pocket_width = 6.0
pocket_height = 8.0
pocket_depth = 30.0
pocket_offset_from_bottom = 5.0
hole_diameter = 6.0
hole_spacing = 20.0
hole_offset_from_inner_corner = 15.0
chamfer_distance = 1.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            l1 = Line((0, 0), (horizontal_leg_length, 0))
            l2 = Line(l1@1, (horizontal_leg_length, leg_thickness))
            l3 = Line(l2@1, (leg_thickness, leg_thickness))
            l4 = Line(l3@1, (leg_thickness, vertical_leg_length))
            l5 = Line(l4@1, (0, vertical_leg_length))
            l6 = Line(l5@1, (0, 0))
        make_face()
    extrude(amount=bracket_thickness)

solid_body = p.part

pocket = Pos(leg_thickness/2, pocket_offset_from_bottom + pocket_depth/2, bracket_thickness/2) * Box(pocket_width, pocket_depth, pocket_height)
solid_body = solid_body - pocket

for i in range(3):
    hx = hole_offset_from_inner_corner + i * hole_spacing
    hy = leg_thickness / 2
    hz = bracket_thickness / 2
    hole = Pos(hx, hy, hz) * Rot(90, 0, 0) * Cylinder(hole_diameter/2, leg_thickness)
    solid_body = solid_body - hole

solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_distance)

part = solid_body
part.name = "L_Bracket"
export_step(part, "output.step")