from build123d import *

leg_length_long = 80.0
leg_length_short = 60.0
thickness = 8.0
bracket_depth = 10.0
pocket_width = 30.0
pocket_height = 6.0
pocket_depth = 8.0
hole_diameter = 6.0
hole_spacing = 20.0
hole_offset_from_end = 20.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0,0), (leg_length_long,0), (leg_length_long,thickness),
                     (thickness,thickness), (thickness,leg_length_short),
                     (0,leg_length_short), close=True)
        make_face()
    extrude(amount=bracket_depth)

solid = p.part

pocket_box = Box(pocket_depth, pocket_width, pocket_height)
solid = solid - Pos(pocket_depth/2, leg_length_short/2, bracket_depth/2) * pocket_box

hole_cyl = Cylinder(hole_diameter/2, leg_length_short + 10)
for x in [hole_offset_from_end, hole_offset_from_end + hole_spacing, hole_offset_from_end + 2*hole_spacing]:
    solid = solid - Pos(x, leg_length_short/2, bracket_depth/2) * Rot(90, 0, 0) * hole_cyl

part = solid
part.name = "L_Bracket"
export_step(part, "output.step")