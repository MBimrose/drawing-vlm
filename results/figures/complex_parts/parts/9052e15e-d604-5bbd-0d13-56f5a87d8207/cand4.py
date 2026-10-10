from build123d import *

leg_length_long = 80.0
leg_length_short = 70.0
bracket_thickness = 8.0
bracket_depth = 20.0
rib_thickness = 3.0
rib_height = 6.0
inner_fillet_radius = 2.0
hole_diameter = 5.0
hole_counterbore_diameter = 8.0
hole_counterbore_depth = 3.0
hole_spacing = 30.0
hole_offset_from_inner = 15.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0, 0), (leg_length_long, 0), (leg_length_long, bracket_thickness),
                     (bracket_thickness, bracket_thickness), (bracket_thickness, leg_length_short),
                     (0, leg_length_short), close=True)
        make_face()
    extrude(amount=bracket_depth)

solid_body = p.part

rib = Pos(rib_thickness/2, leg_length_short + bracket_thickness/2, bracket_depth/2) * Box(rib_thickness, bracket_thickness, rib_height)
solid_body = solid_body + rib

inner_edges = [e for e in solid_body.edges() if abs(e.center().X) < 1e-6 and abs(e.center().Y) < 1e-6]
solid_body = fillet(inner_edges, inner_fillet_radius)

for x, y in [(hole_offset_from_inner, bracket_thickness/2), (hole_offset_from_inner + hole_spacing, bracket_thickness/2)]:
    solid_body = solid_body - Pos(x, y, 0) * Cylinder(hole_diameter/2, bracket_depth + 1)
    solid_body = solid_body - Pos(x, y, 0) * Cylinder(hole_counterbore_diameter/2, hole_counterbore_depth)

part = solid_body
part.name = "L_bracket_with_rib"
export_step(part, "output.step")