from build123d import *

leg_length = 80.0
leg_width = 60.0
thickness = 8.0
extrude_depth = 15.0
fillet_radius = 4.0
hole_diameter = 6.0
hole_spacing = 20.0
hole_offset = 20.0
pocket_width = 10.0
pocket_depth = 12.0
pocket_height = 4.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            l1 = Line((0, 0), (leg_width, 0))
            l2 = Line(l1 @ 1, (leg_width, thickness))
            l3 = Line(l2 @ 1, (thickness, thickness))
            l4 = Line(l3 @ 1, (thickness, leg_length))
            l5 = Line(l4 @ 1, (0, leg_length))
            l6 = Line(l5 @ 1, (0, 0))
        make_face()
    extrude(amount=extrude_depth)

solid_body = p.part

inner_edges = [e for e in solid_body.edges().filter_by(Axis.Z)
               if abs(e.center().X - thickness) < 1e-3 and abs(e.center().Y - thickness) < 1e-3]
solid_body = fillet(inner_edges, fillet_radius)

for i in range(3):
    y = hole_offset + i * hole_spacing
    solid_body = solid_body - Pos(thickness / 2, y, extrude_depth / 2) * Cylinder(hole_diameter / 2, extrude_depth)

solid_body = solid_body - Pos(leg_width - thickness / 2, thickness / 2, extrude_depth / 2) * Cylinder(hole_diameter / 2, extrude_depth)

solid_body = solid_body - Pos(leg_width - pocket_width / 2, thickness / 2, extrude_depth - pocket_height / 2) * Box(pocket_width, pocket_depth, pocket_height)

part = solid_body
part.name = "L_bracket"
export_step(part, "output.step")