from build123d import *

leg_length = 70.0
leg_height = 60.0
leg_thickness = 8.0
bracket_depth = 12.0
chamfer_size = 2.0
hole_diameter = 6.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0, 0), (leg_length + leg_thickness, 0), (leg_length + leg_thickness, leg_thickness),
                     (leg_thickness, leg_thickness), (leg_thickness, leg_height), (0, leg_height), close=True)
        make_face()
    extrude(amount=bracket_depth)

solid_body = p.part

inner_edges = [e for e in solid_body.edges() if abs(e.center().X - leg_thickness) < 0.1 and abs(e.center().Y - leg_thickness) < 0.1]
solid_body = chamfer(inner_edges, chamfer_size)

solid_body = solid_body - Pos(leg_thickness/2, leg_height/2, bracket_depth/2) * Cylinder(hole_diameter/2, bracket_depth)
solid_body = solid_body - Pos(leg_length/2 + leg_thickness/2, leg_thickness/2, bracket_depth/2) * Cylinder(hole_diameter/2, bracket_depth)

part = solid_body
part.name = "L_Bracket"
export_step(part, "output.step")