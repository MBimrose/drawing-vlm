from build123d import *

horizontal_leg_length = 80.0
vertical_leg_length = 60.0
leg_thickness = 8.0
bracket_depth = 12.0
rib_thickness = 6.0
hole_diameter = 6.0
hole_offset_horizontal = 40.0
hole_offset_vertical = 30.0
chamfer_distance = 2.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0,0), (horizontal_leg_length, 0), (horizontal_leg_length, leg_thickness),
                     (leg_thickness, leg_thickness), (leg_thickness, vertical_leg_length),
                     (0, vertical_leg_length), close=True)
        make_face()
    extrude(amount=bracket_depth)
base = p.part

with BuildPart() as p2:
    with BuildSketch() as sk2:
        with BuildLine() as bl2:
            Polyline((0,0), (rib_thickness, 0), (0, rib_thickness), close=True)
        make_face()
    extrude(amount=bracket_depth)
rib = p2.part

solid_body = base + rib

solid_body = solid_body - Pos(hole_offset_horizontal, leg_thickness/2, bracket_depth/2) * Cylinder(hole_diameter/2, bracket_depth)
solid_body = solid_body - Pos(leg_thickness/2, hole_offset_vertical, bracket_depth/2) * Cylinder(hole_diameter/2, bracket_depth)

inner_edges = [e for e in solid_body.edges().filter_by(Axis.Z) if abs(e.center().X - leg_thickness) < 0.1 and abs(e.center().Y - leg_thickness) < 0.1]
solid_body = chamfer(inner_edges, chamfer_distance)

part = solid_body
part.name = "L_Bracket"
export_step(part, "output.step")