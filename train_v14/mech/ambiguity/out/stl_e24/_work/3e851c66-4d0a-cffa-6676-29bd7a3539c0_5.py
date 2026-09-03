from build123d import *

leg_length_x = 80.0
leg_length_y = 60.0
thickness = 6.0
depth = 30.0
inner_fillet_radius = 10.0
hole_diameter = 8.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0,0), (leg_length_x, 0), (leg_length_x, thickness), (thickness, thickness), (thickness, leg_length_y), (0, leg_length_y), close=True)
        make_face()
    extrude(amount=depth)

solid_body = p.part
inner_edges = [e for e in solid_body.edges().filter_by(Axis.Z) if abs(e.center().X - thickness) < 0.1 and abs(e.center().Y - thickness) < 0.1]
solid_body = fillet(inner_edges, inner_fillet_radius)

hole_r = hole_diameter / 2
solid_body = solid_body - Pos(leg_length_x/2, thickness/2, 0) * Cylinder(hole_r, depth)
solid_body = solid_body - Pos(thickness/2, leg_length_y/2, 0) * Cylinder(hole_r, depth)

part = solid_body
part.name = "L_Bracket"
export_step(part, "output.step")