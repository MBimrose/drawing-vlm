from build123d import *

leg_length = 80.0
leg_width = 20.0
leg_thickness = 8.0
flange_length = 40.0
flange_width = 28.0
pocket_width = 5.0
pocket_depth = 6.0
pocket_spacing = 15.0
pocket_count = 3
hole_diameter = 5.0
chamfer_size = 1.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0, 0), (leg_length, 0), (leg_length, leg_width),
                     (flange_length, leg_width), (flange_length, leg_width + flange_width),
                     (0, leg_width + flange_width), close=True)
        make_face()
    extrude(amount=leg_thickness)

solid_body = p.part

vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = chamfer(vertical_edges, chamfer_size)

for i in range(pocket_count):
    x = flange_length + pocket_spacing / 2 + i * pocket_spacing
    y = leg_width / 2
    pocket = Pos(x, y, leg_thickness - pocket_depth / 2) * Box(pocket_width, pocket_depth, pocket_depth)
    solid_body = solid_body - pocket

hole_x = flange_length / 2
hole_y = leg_width + flange_width / 2
hole = Pos(hole_x, hole_y, leg_thickness / 2) * Cylinder(hole_diameter / 2, leg_thickness)
solid_body = solid_body - hole

part = solid_body
part.name = "L_bracket_with_pockets_and_hole"
export_step(part, "output.step")