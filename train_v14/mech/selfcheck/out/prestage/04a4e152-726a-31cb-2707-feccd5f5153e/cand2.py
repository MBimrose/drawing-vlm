from build123d import *

leg_length = 50.0
leg_height = 30.0
leg_thickness = 10.0
bracket_thickness = 12.0
relief_cut_width = 20.0
relief_cut_depth = 8.0
hole_diameter = 6.0
hole_depth = 8.0
chamfer_distance = 1.0
pocket_width = 6.0
pocket_height = 8.0
pocket_depth = 6.0
pocket_offset = 5.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0, 0), (leg_length, 0), (leg_length, leg_thickness),
                     (leg_thickness, leg_thickness), (leg_thickness, leg_height),
                     (0, leg_height), close=True)
        make_face()
    extrude(amount=bracket_thickness)

solid_body = p.part

with BuildPart() as relief_p:
    with BuildSketch() as relief_sk:
        with BuildLine() as relief_bl:
            Polyline((leg_thickness, leg_thickness),
                     (leg_thickness + relief_cut_width, leg_thickness),
                     (leg_thickness + relief_cut_width, leg_thickness + relief_cut_depth),
                     (leg_thickness, leg_thickness + relief_cut_depth), close=True)
        make_face()
    extrude(amount=bracket_thickness)

solid_body = solid_body - relief_p.part

hole_x = leg_thickness / 2
hole_y = leg_height - hole_depth / 2
solid_body = solid_body - Pos(hole_x, hole_y, bracket_thickness - hole_depth / 2) * Cylinder(hole_diameter / 2, hole_depth)

pocket1_x = leg_length / 2
pocket1_y = leg_thickness / 2
solid_body = solid_body - Pos(pocket1_x, pocket1_y, bracket_thickness - pocket_depth / 2) * Box(pocket_width, pocket_height, pocket_depth)

pocket2_x = leg_thickness / 2
pocket2_y = leg_height / 2
solid_body = solid_body - Pos(pocket2_x, pocket2_y, bracket_thickness - pocket_depth / 2) * Box(pocket_width, pocket_height, pocket_depth)

part = solid_body
part.name = "L_bracket"
export_step(part, "output.step")