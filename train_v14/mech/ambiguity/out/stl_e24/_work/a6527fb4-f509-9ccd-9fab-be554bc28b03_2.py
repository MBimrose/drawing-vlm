from build123d import *

vertical_leg_length = 80.0
horizontal_leg_length = 60.0
thickness = 8.0
bracket_depth = 15.0
inner_fillet_radius = 3.0
hole_diameter = 6.0
pocket_width = 30.0
pocket_depth = 10.0
pocket_height = 4.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0, 0), (horizontal_leg_length, 0), (horizontal_leg_length, thickness),
                     (thickness, thickness), (thickness, vertical_leg_length), (0, vertical_leg_length), close=True)
        make_face()
    extrude(amount=bracket_depth)

solid_body = p.part

inner_edges = [e for e in solid_body.edges().filter_by(Axis.Z) if abs(e.center().X - thickness) < 0.1 and abs(e.center().Y - thickness) < 0.1]
solid_body = fillet(inner_edges, inner_fillet_radius)

hole_r = hole_diameter / 2
for y in [vertical_leg_length / 3, 2 * vertical_leg_length / 3, vertical_leg_length / 2]:
    solid_body = solid_body - Pos(thickness / 2, y, bracket_depth / 2) * Cylinder(hole_r, bracket_depth)

solid_body = solid_body - Pos(horizontal_leg_length - thickness / 2, thickness / 2, bracket_depth / 2) * Cylinder(hole_r, bracket_depth)

pocket = Pos(horizontal_leg_length / 2, thickness / 2, bracket_depth - pocket_height / 2) * Box(pocket_width, pocket_depth, pocket_height)
solid_body = solid_body - pocket

part = solid_body
part.name = "L_Bracket"
export_step(part, "output.step")