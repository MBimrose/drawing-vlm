from build123d import *

block_length = 80.0
block_width = 30.0
block_height = 20.0
wall_thickness = 1.0
slot_width = 4.0
slot_length = 25.0
hole_diameter = 4.0
hole_spacing = 12.0
chamfer_size = 0.5

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            l1 = Line((0, 0), (block_length, 0))
            l2 = Line(l1 @ 1, (block_length, block_width))
            arc = ThreePointArc(l2 @ 1, (block_length / 2, block_width + 5), (0, block_width))
            l3 = Line(arc @ 1, (0, 0))
        make_face()
    extrude(amount=block_height)

solid_body = p.part

bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[bottom_face])

slot_box = Pos(block_length - slot_width / 2, block_width, block_height) * Box(slot_width, slot_width, slot_length)
solid_body = solid_body - slot_box

for i in range(3):
    x = block_length / 2 + (i - 1) * hole_spacing
    y = block_width / 2
    hole = Pos(x, y, block_height) * Cylinder(hole_diameter / 2, block_height)
    solid_body = solid_body - hole

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
top_edges = top_face.edges()
solid_body = chamfer(top_edges, chamfer_size)

part = solid_body
part.name = "shelled_block_with_slot_and_holes"
export_step(part, "output.step")