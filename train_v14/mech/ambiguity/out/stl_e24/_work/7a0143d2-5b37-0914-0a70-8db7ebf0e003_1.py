from build123d import *

vertical_leg_height = 70.0
horizontal_leg_length = 80.0
thickness = 10.0
rib_width = 12.0
rib_height = 12.0
slot_width = 5.0
slot_length = 30.0
slot_depth = thickness
hole_diameter = 5.0
hole_spacing = 40.0
chamfer_distance = 1.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            l1 = Line((0, 0), (thickness, 0))
            l2 = Line(l1 @ 1, (thickness, vertical_leg_height - thickness))
            l3 = Line(l2 @ 1, (horizontal_leg_length, vertical_leg_height - thickness))
            l4 = Line(l3 @ 1, (horizontal_leg_length, vertical_leg_height))
            l5 = Line(l4 @ 1, (0, vertical_leg_height))
            l6 = Line(l5 @ 1, (0, 0))
        make_face()
    extrude(amount=thickness)

solid_body = p.part

with BuildPart() as rib_p:
    with BuildSketch() as rib_sk:
        with BuildLine() as rib_bl:
            rl1 = Line((0, 0), (rib_width, 0))
            rl2 = Line(rl1 @ 1, (0, rib_height))
            rl3 = Line(rl2 @ 1, (0, 0))
        make_face()
    extrude(amount=thickness)

solid_body = solid_body + rib_p.part

slot_box = Box(slot_width, slot_depth, slot_length)
slot_box = Pos(horizontal_leg_length / 2, vertical_leg_height - slot_depth / 2, thickness / 2) * slot_box
solid_body = solid_body - slot_box

for x in [horizontal_leg_length / 2 - hole_spacing / 2, horizontal_leg_length / 2 + hole_spacing / 2]:
    hole = Rot(90, 0, 0) * Cylinder(hole_diameter / 2, vertical_leg_height + 10)
    hole = Pos(x, vertical_leg_height / 2, thickness / 2) * hole
    solid_body = solid_body - hole

outer_edges = solid_body.edges().filter_by(Axis.Z).sort_by(Axis.X)[:1]
solid_body = chamfer(outer_edges, chamfer_distance)

part = solid_body
part.name = "L_Bracket"
export_step(part, "output.step")