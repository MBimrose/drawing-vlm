from build123d import *

lever_length = 80.0
lever_width = 20.0
lever_thickness = 10.0
notch_width = 20.0
notch_depth = 8.0
chamfer_size = 1.0
hole_diameter = 4.0
hole_spacing = 12.0
hole_offset = 15.0
slot_width = 2.0
slot_length = lever_length - 20.0
rib_height = 3.0
rib_width = 5.0
rib_offset = 5.0
pocket_width = 8.0
pocket_depth = 5.0
pocket_offset = 30.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            l1 = Line((0, 0), (lever_length, 0))
            l2 = Line(l1 @ 1, (lever_length, lever_width - notch_depth))
            l3 = Line(l2 @ 1, (lever_length - notch_width, lever_width))
            l4 = Line(l3 @ 1, (0, lever_width))
            l5 = Line(l4 @ 1, (0, 0))
        make_face()
    extrude(amount=lever_thickness)

solid_body = p.part

chamfer_edges = solid_body.edges().filter_by(Axis.Z).sort_by(Axis.X)[-2:]
solid_body = chamfer(chamfer_edges, chamfer_size)

for i in range(3):
    x = hole_offset + i * hole_spacing
    y = lever_width / 2
    solid_body = solid_body - Pos(x, y, lever_thickness / 2) * Cylinder(hole_diameter / 2, lever_thickness)

slot_box = Pos(lever_length / 2, lever_width / 2, lever_thickness * 3 / 4) * Box(slot_length, slot_width, lever_thickness / 2)
solid_body = solid_body - slot_box

rib_box = Pos(lever_length - rib_offset - rib_width / 2, lever_width / 2, lever_thickness / 4) * Box(rib_width, rib_height, lever_thickness / 2)
solid_body = solid_body + rib_box

pocket_box = Pos(pocket_offset, lever_width / 2, lever_thickness * 3 / 4) * Box(pocket_width, pocket_depth, lever_thickness / 2)
solid_body = solid_body - pocket_box

part = solid_body
part.name = "lever"
export_step(part, "output.step")