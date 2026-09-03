from build123d import *

leg_length = 80.0
leg_width = 12.0
leg_height = 70.0
thickness = 8.0
fillet_radius = 1.0
hole_diameter = 6.0
hole_depth = 5.0
hole_spacing = 10.0
pocket_width = 10.0
pocket_height = 6.0
pocket_offset = 20.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0, 0), (leg_length, 0), (leg_length, leg_width),
                     (leg_width, leg_width), (leg_width, leg_height),
                     (0, leg_height), close=True)
        make_face()
    extrude(amount=thickness)

solid_body = p.part
solid_body = fillet(solid_body.edges().filter_by(Axis.Z), fillet_radius)

hole_r = hole_diameter / 2
for y_pos in [leg_width/2 - hole_spacing/2, leg_width/2 + hole_spacing/2]:
    solid_body = solid_body - Pos(leg_length - hole_depth/2, y_pos, thickness/2) * Rot(0, 90, 0) * Cylinder(hole_r, hole_depth)

pocket_center_y = leg_height - pocket_offset - pocket_height/2
solid_body = solid_body - Pos(leg_width/2, pocket_center_y, thickness/2) * Box(pocket_width, pocket_height, thickness)

part = solid_body
part.name = "L_bracket"
export_step(part, "output.step")