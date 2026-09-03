from build123d import *

leg_length = 80.0
leg_width = 30.0
thickness = 8.0
fillet_radius = 3.0
hole_diameter = 6.0
hole_offset = 10.0
notch_width = 15.0
notch_depth = 8.0
notch_offset = 10.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0, 0), (leg_length, 0), (leg_length, leg_width),
                     (leg_width, leg_width), (leg_width, leg_width + leg_width),
                     (0, leg_width + leg_width), close=True)
        make_face()
    extrude(amount=thickness)

solid_body = p.part

inner_edges = [e for e in solid_body.edges().filter_by(Axis.Z)
               if abs(e.center().X - leg_width) < 1e-3 and abs(e.center().Y - leg_width) < 1e-3]
solid_body = fillet(inner_edges, fillet_radius)

notch = Pos(notch_offset + notch_width/2, leg_width + leg_width/2, thickness/2) * Box(notch_width, notch_depth, thickness)
solid_body = solid_body - notch

hole_positions = [
    (hole_offset, hole_offset),
    (leg_width - hole_offset, leg_width - hole_offset),
    (hole_offset, leg_width + leg_width - hole_offset),
    (leg_width - hole_offset, leg_width + leg_width - hole_offset),
    (leg_length - hole_offset, hole_offset),
    (leg_length - hole_offset, leg_width - hole_offset),
]
for x, y in hole_positions:
    solid_body = solid_body - Pos(x, y, thickness/2) * Cylinder(hole_diameter/2, thickness)

part = solid_body
part.name = "L_bracket"
export_step(part, "output.step")