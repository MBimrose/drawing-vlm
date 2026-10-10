from build123d import *

leg_width = 20.0
leg_thickness = 8.0
vertical_leg_length = 70.0
horizontal_leg_length = 80.0
fillet_radius = 4.0
pocket_width = 12.0
pocket_length = 30.0
pocket_depth = 6.0
countersink_diameter = 5.0
countersink_angle = 82.0
countersink_depth = 3.0
rib_width = 4.0
rib_height = 20.0
rib_thickness = 2.0
rib_spacing = 10.0
rib_count = 3

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            l1 = Line((0, 0), (horizontal_leg_length, 0))
            l2 = Line(l1 @ 1, (horizontal_leg_length, vertical_leg_length))
            l3 = Line(l2 @ 1, (horizontal_leg_length - leg_width, vertical_leg_length))
            l4 = Line(l3 @ 1, (horizontal_leg_length - leg_width, leg_width))
            l5 = Line(l4 @ 1, (0, leg_width))
            l6 = Line(l5 @ 1, (0, 0))
        make_face()
    extrude(amount=leg_thickness)

solid_body = p.part

z_edges = solid_body.edges().filter_by(Axis.Z)
max_x_edges = z_edges.sort_by(Axis.X)[-2:]
solid_body = fillet(max_x_edges, fillet_radius)

pocket = Pos(leg_width + pocket_width/2, leg_width/2, leg_thickness - pocket_depth/2) * Box(pocket_width, pocket_length, pocket_depth)
solid_body = solid_body - pocket

csk = Pos(horizontal_leg_length - leg_width/2, vertical_leg_length/2, leg_thickness) * CounterSinkHole(countersink_diameter/2, countersink_depth/2, countersink_angle)
solid_body = solid_body - csk

for i in range(rib_count):
    x_pos = leg_width + rib_spacing/2 + i * rib_spacing
    rib = Pos(x_pos, leg_width/2, rib_thickness/2) * Box(rib_width, rib_height, rib_thickness)
    solid_body = solid_body + rib

part = solid_body
part.name = "L_Bracket"
export_step(part, "output.step")