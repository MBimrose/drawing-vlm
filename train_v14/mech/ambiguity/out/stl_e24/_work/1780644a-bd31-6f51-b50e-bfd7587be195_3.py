from build123d import *

horizontal_length = 80.0
vertical_height = 60.0
leg_thickness = 12.0
bracket_thickness = 10.0
pocket_width = 6.0
pocket_depth = 4.0
pocket_height = 6.0
hole_diameter = 5.0
hole_spacing = 30.0
hole_offset_from_bottom = 15.0
notch_width = 8.0
notch_depth = 3.0
notch_height = 4.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0,0), (horizontal_length, 0), (horizontal_length, leg_thickness),
                     (leg_thickness, leg_thickness), (leg_thickness, vertical_height),
                     (0, vertical_height), close=True)
        make_face()
    extrude(amount=bracket_thickness)

solid = p.part

notch = Pos(leg_thickness - notch_depth/2, leg_thickness - notch_depth/2, bracket_thickness/2) * Box(notch_depth, notch_depth, notch_height)
solid = solid - notch

pocket = Pos(pocket_depth/2, vertical_height/2, bracket_thickness/2) * Box(pocket_depth, pocket_width, pocket_height)
solid = solid - pocket

for y in [hole_offset_from_bottom, hole_offset_from_bottom + hole_spacing]:
    hole = Pos(0, y, bracket_thickness/2) * Rot(0, 90, 0) * Cylinder(hole_diameter/2, bracket_thickness)
    solid = solid - hole

part = solid
part.name = "L_Bracket"
export_step(part, "output.step")