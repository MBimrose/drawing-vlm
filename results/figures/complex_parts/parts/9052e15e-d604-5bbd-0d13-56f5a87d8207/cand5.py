from build123d import *

leg_length = 80.0
leg_thickness = 8.0
bracket_width = 20.0
rib_thickness = 4.0
rib_height = 6.0
fillet_radius = 2.0
hole_diameter = 5.0
cbore_diameter = 8.0
cbore_depth = 3.0
hole_spacing = 30.0
hole_offset = 15.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0, 0), (leg_length, 0), (leg_length, leg_thickness),
                     (leg_thickness, leg_thickness), (leg_thickness, leg_length),
                     (0, leg_length), close=True)
        make_face()
    extrude(amount=bracket_width)

solid_body = p.part

rib = Pos(rib_thickness/2, leg_length + bracket_width/2, bracket_width/2) * Box(rib_thickness, bracket_width, rib_height)
solid_body = solid_body + rib

inner_edges = [e for e in solid_body.edges().filter_by(Axis.Z) if abs(e.center().X) < 1e-6 and abs(e.center().Y) < 1e-6]
solid_body = fillet(inner_edges, fillet_radius)

for x, y in [(leg_length/2 - hole_spacing/2, hole_offset), (leg_length/2 + hole_spacing/2, hole_offset)]:
    solid_body = solid_body - Pos(x, y, 0) * Cylinder(hole_diameter/2, bracket_width + 1)
    solid_body = solid_body - Pos(x, y, 0) * Cylinder(cbore_diameter/2, cbore_depth)

part = solid_body
part.name = "L_bracket_with_rib"
export_step(part, "output.step")