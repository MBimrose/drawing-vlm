from build123d import *

leg_length_long = 80.0
leg_length_short = 55.0
leg_thickness = 12.0
bracket_depth = 10.0
inner_fillet_radius = 2.0
hole_diameter = 5.0
hole_offset_long = 30.0
hole_offset_short = 20.0
gusset = True
gusset_thickness = 4.0

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
solid_body = fillet(inner_edges, inner_fillet_radius)

solid_body = solid_body - Pos(hole_offset_long, leg_thickness/2, bracket_depth/2) * Cylinder(hole_diameter/2, bracket_depth)
solid_body = solid_body - Pos(leg_thickness/2, hole_offset_short, bracket_depth/2) * Cylinder(hole_diameter/2, bracket_depth)

if gusset:
    with BuildPart() as gp:
        with BuildSketch() as gsk:
            with BuildLine() as gbl:
                Polyline((leg_thickness, leg_thickness),
                         (leg_thickness + gusset_thickness, leg_thickness),
                         (leg_thickness, leg_thickness + gusset_thickness), close=True)
            make_face()
        extrude(amount=bracket_depth)
    solid_body = solid_body + gp.part

part = solid_body
part.name = "L_bracket"
export_step(part, "output.step")