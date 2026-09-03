from build123d import *

leg_length_long = 80.0
leg_length_short = 60.0
leg_thickness = 10.0
bracket_depth = 10.0
inner_chamfer = 2.0
blind_hole_diameter = 5.0
blind_hole_depth = 5.0
blind_hole_spacing = 20.0
blind_hole_offset = 15.0
through_hole_diameter = 6.0
through_hole_offset = 15.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0, 0), (leg_length_long, 0), (leg_length_long, leg_thickness),
                     (leg_thickness, leg_thickness), (leg_thickness, leg_length_short),
                     (0, leg_length_short), close=True)
        make_face()
    extrude(amount=bracket_depth)

solid_body = p.part

inner_edges = [e for e in solid_body.edges().filter_by(Axis.Z)
               if abs(e.center().X - leg_thickness) < 1e-3 and abs(e.center().Y - leg_thickness) < 1e-3]
solid_body = chamfer(inner_edges, inner_chamfer)

for i in range(3):
    x = blind_hole_offset + i * blind_hole_spacing
    y = leg_thickness / 2
    solid_body = solid_body - Pos(x, y, bracket_depth - blind_hole_depth / 2) * Cylinder(blind_hole_diameter / 2, blind_hole_depth)

solid_body = solid_body - Pos(leg_thickness / 2, through_hole_offset, bracket_depth / 2) * Rot(90, 0, 0) * Cylinder(through_hole_diameter / 2, leg_length_short)

part = solid_body
part.name = "L_bracket"
export_step(part, "output.step")