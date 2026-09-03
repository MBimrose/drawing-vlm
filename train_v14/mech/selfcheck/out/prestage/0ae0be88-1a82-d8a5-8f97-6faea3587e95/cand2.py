from build123d import *

leg_length = 80.0
leg_height = 55.0
leg_thickness = 12.0
bracket_thickness = 10.0
fillet_radius = 3.0
hole_diameter = 5.0
hole_offset = 20.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0,0), (leg_length,0), (leg_length,leg_thickness), (leg_thickness,leg_thickness), (leg_thickness,leg_height), (0,leg_height), close=True)
        make_face()
    extrude(amount=bracket_thickness)

solid_body = p.part

inner_edges = [e for e in solid_body.edges().filter_by(Axis.Z) if abs(e.center().X - leg_thickness) < 1e-3 and abs(e.center().Y - leg_thickness) < 1e-3]
solid_body = fillet(inner_edges, fillet_radius)

solid_body = solid_body - Pos(leg_length - hole_offset, leg_thickness/2, bracket_thickness/2) * Cylinder(hole_diameter/2, bracket_thickness)
solid_body = solid_body - Pos(leg_thickness/2, leg_height - hole_offset, bracket_thickness/2) * Cylinder(hole_diameter/2, bracket_thickness)

part = solid_body
part.name = "L_bracket"
export_step(part, "output.step")