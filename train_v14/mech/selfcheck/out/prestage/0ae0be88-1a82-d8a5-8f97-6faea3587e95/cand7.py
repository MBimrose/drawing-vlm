from build123d import *

long_leg = 80.0
short_leg = 55.0
leg_thickness = 12.0
bracket_depth = 10.0
inner_fillet_radius = 3.0
outer_chamfer = 0.8
hole_diameter = 5.0
hole_offset_long = 30.0
hole_offset_short = 20.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0, 0), (long_leg, 0), (long_leg, leg_thickness),
                     (leg_thickness, leg_thickness), (leg_thickness, short_leg),
                     (0, short_leg), close=True)
        make_face()
    extrude(amount=bracket_depth)

solid = p.part

inner_edges = [e for e in solid.edges().filter_by(Axis.Z)
               if abs(e.center().X - leg_thickness) < 1e-3 and abs(e.center().Y - leg_thickness) < 1e-3]
solid = fillet(inner_edges, inner_fillet_radius)

solid = solid - Pos(hole_offset_long, leg_thickness / 2, bracket_depth / 2) * Cylinder(hole_diameter / 2, bracket_depth + 1)
solid = solid - Pos(leg_thickness / 2, hole_offset_short, bracket_depth / 2) * Cylinder(hole_diameter / 2, bracket_depth + 1)

part = solid
part.name = "L_Bracket"
export_step(part, "output.step")