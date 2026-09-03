from build123d import *

leg_length = 80.0
leg_height = 60.0
thickness = 6.0
extrude_depth = 30.0
fillet_radius = 10.0
rib_thickness = 4.0
rib_height = 20.0
hole_diameter = 8.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0,0), (leg_length,0), (leg_length,thickness), (thickness,thickness), (thickness,leg_height), (0,leg_height), close=True)
        make_face()
    extrude(amount=extrude_depth)

solid_body = p.part

inner_edges = [e for e in solid_body.edges().filter_by(Axis.Z) if abs(e.center().X - thickness) < 1e-3 and abs(e.center().Y - thickness) < 1e-3]
solid_body = fillet(inner_edges, fillet_radius)

with BuildPart() as rib_p:
    with BuildSketch() as rib_sk:
        with BuildLine() as rib_bl:
            Polyline((0,0), (rib_height,0), (0,rib_height), close=True)
        make_face()
    extrude(amount=extrude_depth)

solid_body = solid_body + rib_p.part

solid_body = solid_body - Pos(leg_length/2, thickness/2, 0) * Cylinder(hole_diameter/2, extrude_depth)
solid_body = solid_body - Pos(thickness/2, leg_height/2, 0) * Cylinder(hole_diameter/2, extrude_depth)

part = solid_body
part.name = "L_bracket"
export_step(part, "output.step")