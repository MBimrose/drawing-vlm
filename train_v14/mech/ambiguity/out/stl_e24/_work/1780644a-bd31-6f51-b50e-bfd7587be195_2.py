from build123d import *

long_leg = 80.0
short_leg = 60.0
leg_width = 12.0
thickness = 10.0
rib_width = 8.0
hole_diameter = 5.0
hole_spacing = 30.0
chamfer_size = 1.0
pocket_width = 6.0
pocket_depth = 4.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0, 0), (long_leg, 0), (long_leg, leg_width), (leg_width, leg_width), (leg_width, short_leg), (0, short_leg), close=True)
        make_face()
    extrude(amount=thickness)

solid_body = p.part

with BuildPart() as rib_p:
    with BuildSketch() as rib_sk:
        with BuildLine() as rib_bl:
            Polyline((0, 0), (rib_width, 0), (0, rib_width), close=True)
        make_face()
    extrude(amount=thickness)

solid_body = solid_body + rib_p.part

hole_r = hole_diameter / 2
for y in [short_leg/2 - hole_spacing/2, short_leg/2 + hole_spacing/2]:
    solid_body = solid_body - Pos(0, y, thickness/2) * Rot(0, 90, 0) * Cylinder(hole_r, thickness)

solid_body = solid_body - Pos(leg_width/2, short_leg/2, thickness/2) * Box(pocket_depth, pocket_width, pocket_width)

part = solid_body
part.name = "L_Bracket"
export_step(part, "output.step")