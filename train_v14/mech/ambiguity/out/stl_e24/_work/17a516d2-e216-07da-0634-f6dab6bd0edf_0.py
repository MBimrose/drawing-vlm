from build123d import *

horizontal_leg_length = 70.0
vertical_leg_length = 60.0
bracket_thickness = 8.0
bracket_depth = 12.0
inner_fillet_radius = 4.0
hole_diameter = 6.0
hole_offset_from_end = 30.0
rib_width = 6.0
rib_height = 6.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0, 0), (horizontal_leg_length, 0), (horizontal_leg_length, bracket_thickness),
                     (bracket_thickness, bracket_thickness), (bracket_thickness, vertical_leg_length),
                     (0, vertical_leg_length), close=True)
        make_face()
    extrude(amount=bracket_depth)

solid_body = p.part

inner_edges = [e for e in solid_body.edges().filter_by(Axis.Z) if abs(e.center().X - bracket_thickness) < 0.1 and abs(e.center().Y - bracket_thickness) < 0.1]
solid_body = fillet(inner_edges, inner_fillet_radius)

solid_body = solid_body - Pos(hole_offset_from_end, bracket_thickness / 2, bracket_depth / 2) * Cylinder(hole_diameter / 2, bracket_depth)
solid_body = solid_body - Pos(bracket_thickness / 2, hole_offset_from_end, bracket_depth / 2) * Cylinder(hole_diameter / 2, bracket_depth)

with BuildPart() as rib_p:
    with BuildSketch() as rib_sk:
        with BuildLine() as rib_bl:
            Polyline((0, 0), (rib_width, 0), (0, rib_height), close=True)
        make_face()
    extrude(amount=bracket_depth)

solid_body = solid_body + rib_p.part

part = solid_body
part.name = "L_Bracket"
export_step(part, "output.step")