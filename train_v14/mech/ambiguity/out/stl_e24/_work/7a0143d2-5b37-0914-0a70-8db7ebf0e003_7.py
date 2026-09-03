from build123d import *

vertical_height = 70.0
horizontal_length = 70.0
thickness = 10.0
slot_width = 5.0
slot_depth = 6.0
slot_offset = 30.0
hole_diameter = 5.0
hole_spacing = 40.0
chamfer_size = 1.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            l1 = Line((0, 0), (thickness, 0))
            l2 = Line(l1@1, (thickness, vertical_height - thickness))
            l3 = Line(l2@1, (thickness + horizontal_length, vertical_height - thickness))
            l4 = Line(l3@1, (thickness + horizontal_length, vertical_height))
            l5 = Line(l4@1, (0, vertical_height))
            l6 = Line(l5@1, (0, 0))
        make_face()
    extrude(amount=thickness)

solid_body = p.part

slot_box = Pos(thickness + slot_offset, vertical_height - slot_depth/2, thickness/2) * Box(slot_width, slot_depth, thickness)
solid_body = solid_body - slot_box

for i in range(2):
    hx = thickness + hole_spacing/2 + i * hole_spacing
    hz = thickness/2
    hole = Pos(hx, vertical_height, hz) * Rot(90, 0, 0) * Cylinder(hole_diameter/2, 200)
    solid_body = solid_body - hole

bottom_edges = solid_body.edges().sort_by(Axis.Y)[:1]
solid_body = chamfer(bottom_edges, chamfer_size)

part = solid_body
part.name = "L_Bracket"
export_step(part, "output.step")