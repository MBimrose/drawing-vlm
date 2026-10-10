from build123d import *

leg_length = 80.0
leg_width = 30.0
thickness = 15.0
wall_thickness = 4.0
relief_radius = 10.0
fillet_radius = 2.0
hole_diameter = 6.0
hole_offset = 15.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0, 0), (leg_width, 0), (leg_width, leg_length - leg_width),
                     (leg_width + thickness, leg_length - leg_width),
                     (leg_width + thickness, leg_length), (0, leg_length), close=True)
        make_face()
    extrude(amount=thickness)

solid_body = p.part

# Shell with top face as opening
top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face])

# Relief cut: semicircular notch on top edge of vertical leg
relief = Pos(leg_width/2, leg_length, thickness/2) * Cylinder(relief_radius, thickness)
solid_body = solid_body - relief

# Fillet inner corner edges (edges at x=30, y=50)
inner_edges = [e for e in solid_body.edges() if abs(e.center().X - leg_width) < 1 and abs(e.center().Y - (leg_length - leg_width)) < 1]
solid_body = fillet(inner_edges, fillet_radius)

# Through hole in horizontal leg
hole = Pos(hole_offset, hole_offset, thickness/2) * Cylinder(hole_diameter/2, thickness)
solid_body = solid_body - hole

part = solid_body
part.name = "L_bracket"
export_step(part, "output.step")