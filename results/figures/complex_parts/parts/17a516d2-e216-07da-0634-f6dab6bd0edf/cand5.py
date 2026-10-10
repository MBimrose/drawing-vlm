from build123d import *

leg_length_long = 70.0
leg_length_short = 60.0
leg_thickness = 8.0
bracket_depth = 12.0
inner_chamfer = 2.0
hole_diameter = 6.0

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
               if abs(e.center().X - leg_thickness) < 0.1 and abs(e.center().Y - leg_thickness) < 0.1]
solid_body = chamfer(inner_edges, inner_chamfer)

hole_r = hole_diameter / 2
hole_h = bracket_depth + 2
solid_body = solid_body - Pos(leg_length_long / 2, leg_thickness / 2, bracket_depth / 2) * Cylinder(hole_r, hole_h)
solid_body = solid_body - Pos(leg_thickness / 2, leg_length_short / 2, bracket_depth / 2) * Cylinder(hole_r, hole_h)

part = solid_body
part.name = "L_Bracket"
export_step(part, "output.step")