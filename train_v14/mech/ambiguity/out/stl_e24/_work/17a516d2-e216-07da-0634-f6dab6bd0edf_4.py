from build123d import *

leg_long = 70.0
leg_short = 60.0
thickness = 8.0
width = 12.0
chamfer_size = 2.0
hole_diameter = 6.0
rib_height = 4.0
rib_width = 6.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0, 0), (leg_long, 0), (leg_long, thickness), (thickness, thickness), (thickness, leg_short), (0, leg_short), close=True)
        make_face()
    extrude(amount=width)

solid_body = p.part

inner_edges = [e for e in solid_body.edges().filter_by(Axis.Z) if abs(e.center().X - thickness) < 0.1 and abs(e.center().Y - thickness) < 0.1]
solid_body = chamfer(inner_edges, chamfer_size)

hole1 = Pos(leg_long / 2, thickness / 2, width / 2) * Cylinder(hole_diameter / 2, width)
hole2 = Pos(thickness / 2, leg_short / 2, width / 2) * Cylinder(hole_diameter / 2, width)
solid_body = solid_body - hole1 - hole2

rib = Pos(-rib_height / 2, thickness / 2, width / 2) * Box(rib_height, rib_width, width)
solid_body = solid_body + rib

part = solid_body
part.name = "L_Bracket"
export_step(part, "output.step")