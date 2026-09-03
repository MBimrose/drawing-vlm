from build123d import *

leg_length_long = 80.0
leg_length_short = 70.0
leg_width = 30.0
thickness = 8.0
fillet_radius = 4.0
hole_diameter = 6.0
hole_spacing = 30.0
hole_offset = 10.0
slot_width = 15.0
slot_depth = 8.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0, 0), (leg_length_long, 0), (leg_length_long, leg_width),
                     (leg_width, leg_width), (leg_width, leg_length_short),
                     (0, leg_length_short), close=True)
        make_face()
    extrude(amount=thickness)

solid_body = p.part

inner_edges = [e for e in solid_body.edges() if abs(e.center().X - leg_width) < 0.1 and abs(e.center().Y - leg_width) < 0.1]
solid_body = fillet(inner_edges, fillet_radius)

slot = Pos(leg_width/2, leg_length_short/2, thickness/2) * Box(slot_width, slot_depth, thickness)
solid_body = solid_body - slot

hole_r = hole_diameter / 2
for x, y in [(hole_offset, leg_width/2), (hole_offset + hole_spacing, leg_width/2),
             (leg_length_long - hole_offset, leg_width/2), (leg_length_long - hole_offset - hole_spacing, leg_width/2),
             (leg_width/2, hole_offset), (leg_width/2, hole_offset + hole_spacing),
             (leg_width/2, leg_length_short - hole_offset), (leg_width/2, leg_length_short - hole_offset - hole_spacing)]:
    solid_body = solid_body - Pos(x, y, thickness/2) * Cylinder(hole_r, thickness)

part = solid_body
part.name = "L_bracket"
export_step(part, "output.step")