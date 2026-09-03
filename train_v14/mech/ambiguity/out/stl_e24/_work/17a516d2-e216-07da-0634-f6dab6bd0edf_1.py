from build123d import *

vertical_leg_height = 60.0
horizontal_leg_length = 70.0
leg_thickness = 8.0
bracket_depth = 12.0
rib_thickness = 6.0
rib_height = 6.0
hole_diameter = 6.0
chamfer_size = 1.5

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0, 0), (0, vertical_leg_height), (leg_thickness, vertical_leg_height),
                     (leg_thickness, leg_thickness), (horizontal_leg_length + leg_thickness, leg_thickness),
                     (horizontal_leg_length + leg_thickness, 0), close=True)
        make_face()
    extrude(amount=bracket_depth)

solid_body = p.part

with BuildPart() as rib_p:
    with BuildSketch() as rib_sk:
        with BuildLine() as rib_bl:
            Polyline((0, 0), (rib_thickness, 0), (0, rib_height), close=True)
        make_face()
    extrude(amount=bracket_depth)

solid_body = solid_body + rib_p.part

hole1_x = leg_thickness / 2
hole1_y = vertical_leg_height / 2
hole2_x = leg_thickness + horizontal_leg_length / 2
hole2_y = leg_thickness / 2

solid_body = solid_body - Pos(hole1_x, hole1_y, 0) * Cylinder(hole_diameter / 2, bracket_depth * 2)
solid_body = solid_body - Pos(hole2_x, hole2_y, 0) * Cylinder(hole_diameter / 2, bracket_depth * 2)

inner_edges = [e for e in solid_body.edges() if abs(e.center().X - leg_thickness) < 0.1 and abs(e.center().Y - leg_thickness) < 0.1]
solid_body = chamfer(inner_edges, chamfer_size)

part = solid_body
part.name = "L_Bracket"
export_step(part, "output.step")