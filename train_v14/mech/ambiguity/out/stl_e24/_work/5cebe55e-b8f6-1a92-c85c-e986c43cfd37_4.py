from build123d import *

block_length = 80.0
block_width = 30.0
block_height = 20.0
wall_thickness = 1.0
slot_width = 4.0
slot_length = 25.0
slot_depth = 5.0
hole_diameter = 4.0
hole_counterbore_diameter = 6.0
hole_counterbore_depth = 2.0
hole_spacing = 12.0
hole_count = 3
chamfer_size = 0.5

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            l1 = Line((0, 0), (block_length, 0))
            l2 = Line(l1 @ 1, (block_length, block_width))
            arc = ThreePointArc(l2 @ 1, (block_length/2, block_width + 5), (0, block_width))
            l3 = Line(arc @ 1, (0, 0))
        make_face()
    extrude(amount=block_height)

solid_body = p.part
bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[bottom_face])

slot_box = Box(slot_depth, slot_width, slot_length)
slot_box = Pos(block_length - slot_depth/2, block_width, block_height) * slot_box
solid_body = solid_body - slot_box

for i in range(hole_count):
    x = block_length/2 + (i - (hole_count-1)/2) * hole_spacing
    y = block_width/2
    shaft = Cylinder(hole_diameter/2, block_height)
    shaft = Pos(x, y, block_height/2) * shaft
    solid_body = solid_body - shaft
    cbore = Cylinder(hole_counterbore_diameter/2, hole_counterbore_depth)
    cbore = Pos(x, y, block_height - hole_counterbore_depth/2) * cbore
    solid_body = solid_body - cbore

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
top_edges = top_face.edges()
solid_body = chamfer(top_edges, chamfer_size)

part = solid_body
part.name = "shelled_block_with_slot_and_holes"
export_step(part, "output.step")