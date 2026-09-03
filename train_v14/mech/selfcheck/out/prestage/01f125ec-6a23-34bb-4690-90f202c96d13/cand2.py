from build123d import *

leg_length_long = 80.0
leg_length_short = 70.0
leg_width = 30.0
thickness = 8.0
fillet_radius = 4.0
hole_diameter = 6.0
hole_spacing = 30.0
slot_width = 15.0
slot_height = 8.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0, 0), (leg_length_long, 0), (leg_length_long, leg_width),
                     (leg_width, leg_width), (leg_width, leg_length_short),
                     (0, leg_length_short), close=True)
        make_face()
    extrude(amount=thickness)

solid_body = p.part

inner_edges = [e for e in solid_body.edges().filter_by(Axis.Z) if abs(e.center().X - leg_width) < 1e-3 and abs(e.center().Y - leg_width) < 1e-3]
solid_body = fillet(inner_edges, fillet_radius)

slot = Pos(leg_width/2, leg_length_short/2, thickness/2) * Box(slot_width, slot_height, thickness)
solid_body = solid_body - slot

for i in range(3):
    x = leg_width/2 + i * hole_spacing
    y = leg_width/2
    solid_body = solid_body - Pos(x, y, thickness/2) * Cylinder(hole_diameter/2, thickness)

for i in range(3):
    x = leg_width/2
    y = leg_width/2 + i * hole_spacing
    solid_body = solid_body - Pos(x, y, thickness/2) * Cylinder(hole_diameter/2, thickness)

part = solid_body
part.name = "L_Bracket"
export_step(part, "output.step")