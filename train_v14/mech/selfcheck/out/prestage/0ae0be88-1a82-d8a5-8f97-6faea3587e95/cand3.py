from build123d import *

leg_length_long = 80.0
leg_length_short = 55.0
leg_width = 12.0
thickness = 10.0
inner_fillet_radius = 2.0
hole_diameter = 5.0
hole_offset_long = 30.0
hole_offset_short = 20.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0,0), (leg_length_long,0), (leg_length_long,leg_width), (leg_width,leg_width), (leg_width,leg_length_short), (0,leg_length_short), close=True)
        make_face()
    extrude(amount=thickness)

solid = p.part
inner_edges = [e for e in solid.edges().filter_by(Axis.Z) if abs(e.center().X - leg_width) < 0.1 and abs(e.center().Y - leg_width) < 0.1]
solid = fillet(inner_edges, inner_fillet_radius)

solid = solid - Pos(hole_offset_long, leg_width/2, 0) * Cylinder(hole_diameter/2, thickness*2)
solid = solid - Pos(leg_width/2, hole_offset_short, 0) * Cylinder(hole_diameter/2, thickness*2)

part = solid
part.name = "L_Bracket"
export_step(part, "output.step")