from build123d import *

horizontal_leg_length = 70.0
vertical_leg_length = 60.0
leg_thickness = 8.0
bracket_depth = 12.0
inner_chamfer = 2.0
hole_diameter = 6.0
hole_offset = 15.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0, 0), (horizontal_leg_length, 0), (horizontal_leg_length, leg_thickness),
                     (leg_thickness, leg_thickness), (leg_thickness, vertical_leg_length),
                     (0, vertical_leg_length), close=True)
        make_face()
    extrude(amount=bracket_depth)

solid_body = p.part

inner_edges = [e for e in solid_body.edges().filter_by(Axis.Z)
               if abs(e.center().X - leg_thickness) < 0.1 and abs(e.center().Y - leg_thickness) < 0.1]
solid_body = chamfer(inner_edges, inner_chamfer)

hole_r = hole_diameter / 2
hole_h = bracket_depth + 2
solid_body = solid_body - Pos(horizontal_leg_length/2, leg_thickness/2, bracket_depth/2) * Cylinder(hole_r, hole_h)
solid_body = solid_body - Pos(leg_thickness/2, vertical_leg_length/2, bracket_depth/2) * Cylinder(hole_r, hole_h)

part = solid_body
part.name = "L_Bracket"
export_step(part, "output.step")