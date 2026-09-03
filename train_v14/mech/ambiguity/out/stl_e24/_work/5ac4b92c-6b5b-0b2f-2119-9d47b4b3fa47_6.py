from build123d import *

leg_length_long = 80.0
leg_length_short = 60.0
leg_thickness = 10.0
bracket_depth = 12.0
fillet_radius = 2.0
pocket_length = 30.0
pocket_width = 8.0
pocket_depth = 4.0
hole_diameter = 6.0
hole_offset_long = 40.0
hole_offset_short = 30.0
tap_hole_diameter = 4.5
tap_hole_offset = 5.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0, 0), (leg_length_long, 0), (leg_length_long, leg_thickness),
                     (leg_thickness, leg_thickness), (leg_thickness, leg_length_short + leg_thickness),
                     (0, leg_length_short + leg_thickness), close=True)
        make_face()
    extrude(amount=bracket_depth)

solid_body = p.part
solid_body = fillet(solid_body.edges().filter_by(Axis.Z), fillet_radius)

pocket_cx = leg_thickness / 2
pocket_cy = leg_length_short + leg_thickness - pocket_length / 2
solid_body = solid_body - Pos(pocket_cx, pocket_cy, bracket_depth - pocket_depth / 2) * Box(pocket_width, pocket_length, pocket_depth)

solid_body = solid_body - Pos(hole_offset_long, leg_thickness / 2, 0) * Cylinder(hole_diameter / 2, bracket_depth + 1)
solid_body = solid_body - Pos(leg_thickness / 2, hole_offset_short, 0) * Cylinder(hole_diameter / 2, bracket_depth + 1)

tap_cx = leg_thickness / 2
tap_cy = leg_length_short + leg_thickness - tap_hole_offset
solid_body = solid_body - Pos(tap_cx, tap_cy, 0) * Cylinder(tap_hole_diameter / 2, bracket_depth + 1)

part = solid_body
part.name = "L_bracket"
export_step(part, "output.step")