from build123d import *

leg_length = 80.0
leg_height = 55.0
leg_thickness = 12.0
bracket_thickness = 10.0
rib_height = 20.0
rib_thickness = 6.0
hole_diameter = 5.0
hole_offset = 30.0
fillet_radius = 2.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0, 0), (leg_length, 0), (leg_length, leg_thickness),
                     (leg_thickness, leg_thickness), (leg_thickness, leg_height),
                     (0, leg_height), close=True)
        make_face()
    extrude(amount=bracket_thickness)

solid_body = p.part

rib = Pos(leg_thickness - rib_thickness/2, leg_thickness + rib_height/2, bracket_thickness/2) * Box(rib_thickness, rib_height, bracket_thickness)
solid_body = solid_body + rib

hole1 = Pos(hole_offset, leg_thickness/2, bracket_thickness/2) * Cylinder(hole_diameter/2, bracket_thickness)
hole2 = Pos(leg_thickness/2, hole_offset, bracket_thickness/2) * Cylinder(hole_diameter/2, bracket_thickness)
solid_body = solid_body - hole1 - hole2

inner_edges = [e for e in solid_body.edges().filter_by(Axis.Z) if abs(e.center().X - leg_thickness) < 0.1 and abs(e.center().Y - leg_thickness) < 0.1]
solid_body = fillet(inner_edges, fillet_radius)

part = solid_body
part.name = "L_Bracket"
export_step(part, "output.step")