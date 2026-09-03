from build123d import *

long_leg_length = 80.0
short_leg_length = 60.0
leg_thickness = 12.0
bracket_depth = 10.0
rib_thickness = 4.0
hole_diameter = 5.0
hole_spacing = 30.0
pocket_width = 6.0
pocket_depth = 4.0
pocket_offset = 15.0
chamfer_size = 0.8

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0, 0), (long_leg_length, 0), (long_leg_length, leg_thickness),
                     (leg_thickness, leg_thickness), (leg_thickness, short_leg_length),
                     (0, short_leg_length), close=True)
        make_face()
    extrude(amount=bracket_depth)

solid_body = p.part

with BuildPart() as rib_p:
    with BuildSketch() as rib_sk:
        with BuildLine() as rib_bl:
            Polyline((0, 0), (leg_thickness, 0), (0, leg_thickness), close=True)
        make_face()
    extrude(amount=rib_thickness)

solid_body = solid_body + rib_p.part

for y_pos in [short_leg_length/2 - hole_spacing/2, short_leg_length/2 + hole_spacing/2]:
    solid_body = solid_body - Pos(0, y_pos, bracket_depth/2) * Rot(0, 90, 0) * Cylinder(hole_diameter/2, bracket_depth)

pocket = Pos(leg_thickness - pocket_depth/2, short_leg_length/2, bracket_depth/2) * Box(pocket_depth, pocket_width, pocket_width)
solid_body = solid_body - pocket

part = solid_body
part.name = "L_bracket_with_rib"
export_step(part, "output.step")