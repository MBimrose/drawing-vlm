from build123d import *

leg_length = 80.0
leg_thickness = 8.0
bracket_depth = 20.0
inner_fillet_radius = 2.0
rib_width = 20.0
rib_height = 12.0
rib_thickness = 4.0
hole_diameter = 5.0
hole_cbore_diameter = 8.0
hole_cbore_depth = 3.0
hole_spacing = 30.0
hole_offset_from_corner = 25.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0, 0), (leg_length, 0), (leg_length, leg_thickness),
                     (leg_thickness, leg_thickness), (leg_thickness, leg_length),
                     (0, leg_length), close=True)
        make_face()
    extrude(amount=bracket_depth)

solid_body = p.part

inner_edges = [e for e in solid_body.edges() if abs(e.center().X - leg_thickness) < 0.1 and abs(e.center().Y - leg_thickness) < 0.1]
solid_body = fillet(inner_edges, inner_fillet_radius)

rib = Pos(rib_thickness/2, leg_length/2 + rib_width/2, bracket_depth/2) * Box(rib_thickness, rib_width, rib_height)
solid_body = solid_body + rib

for x, y in [(hole_offset_from_corner, leg_thickness/2), (hole_offset_from_corner + hole_spacing, leg_thickness/2)]:
    solid_body = solid_body - Pos(x, y, 0) * Cylinder(hole_diameter/2, bracket_depth + 1)
    solid_body = solid_body - Pos(x, y, 0) * Cylinder(hole_cbore_diameter/2, hole_cbore_depth)

part = solid_body
part.name = "L_bracket_with_rib"
export_step(part, "output.step")