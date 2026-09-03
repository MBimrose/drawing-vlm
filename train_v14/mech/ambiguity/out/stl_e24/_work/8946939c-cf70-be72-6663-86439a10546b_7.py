from build123d import *

vertical_leg_length = 60.0
horizontal_leg_length = 80.0
leg_thickness = 10.0
bracket_depth = 10.0
gusset_thickness = 4.0
hole_diameter = 8.5
hole_spacing = 12.0
hole_edge_offset = 15.0
chamfer_distance = 1.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0, 0), (0, vertical_leg_length), (leg_thickness, vertical_leg_length),
                     (leg_thickness, leg_thickness), (horizontal_leg_length, leg_thickness),
                     (horizontal_leg_length, 0), close=True)
        make_face()
    extrude(amount=bracket_depth)

solid_body = p.part

with BuildPart() as g:
    with BuildSketch() as gsk:
        with BuildLine() as gbl:
            Polyline((leg_thickness, leg_thickness),
                     (leg_thickness + gusset_thickness, leg_thickness),
                     (leg_thickness, leg_thickness + gusset_thickness), close=True)
        make_face()
    extrude(amount=bracket_depth)

solid_body = solid_body + g.part

for i in range(5):
    x = hole_edge_offset + i * hole_spacing
    y = leg_thickness / 2
    solid_body = solid_body - Pos(x, y, bracket_depth / 2) * Cylinder(hole_diameter / 2, bracket_depth + 2)

right_face = solid_body.faces().sort_by(Axis.X)[-1]
right_edges = right_face.edges()
solid_body = chamfer(right_edges, chamfer_distance)

part = solid_body
part.name = "L_Bracket"
export_step(part, "output.step")