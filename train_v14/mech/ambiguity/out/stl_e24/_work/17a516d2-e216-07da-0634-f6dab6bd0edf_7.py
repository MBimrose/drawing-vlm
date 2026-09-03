from build123d import *

leg_length = 70.0
leg_height = 60.0
thickness = 8.0
rib_thickness = 6.0
rib_height = 12.0
bracket_depth = 12.0
hole_diameter = 6.0
chamfer_size = 2.0

with BuildPart() as p:
    with BuildSketch() as s:
        with BuildLine() as l:
            Polyline((0,0), (leg_length, 0), (leg_length, thickness), (thickness, thickness), (thickness, leg_height), (0, leg_height), close=True)
        make_face()
    extrude(amount=bracket_depth)
base = p.part

with BuildPart() as p2:
    with BuildSketch() as s2:
        with BuildLine() as l2:
            Polyline((0,0), (rib_thickness, 0), (0, rib_height), close=True)
        make_face()
    extrude(amount=bracket_depth)
rib = p2.part

solid_body = base + rib

hole1 = Pos(leg_length/2, thickness/2, bracket_depth/2) * Cylinder(hole_diameter/2, bracket_depth)
hole2 = Pos(thickness/2, leg_height/2, bracket_depth/2) * Cylinder(hole_diameter/2, bracket_depth)
solid_body = solid_body - hole1 - hole2

inner_edges = [e for e in solid_body.edges().filter_by(Axis.Z) if abs(e.center().X - thickness) < 0.1 and abs(e.center().Y - thickness) < 0.1]
solid_body = chamfer(inner_edges, chamfer_size)

part = solid_body
part.name = "L_Bracket"
export_step(part, "output.step")