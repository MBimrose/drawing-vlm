from build123d import *

block_length = 80.0
block_width = 40.0
block_height = 20.0
arc_radius = 5.0
slot_width = 8.0
slot_depth = 12.0
hole_diameter = 6.0
hole_spacing = 25.0
hole_offset = 10.0
chamfer_size = 1.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            l1 = Line((0, 0), (block_length - arc_radius, 0))
            a1 = ThreePointArc(l1 @ 1, (block_length, 0), (block_length, arc_radius))
            l2 = Line(a1 @ 1, (block_length, block_width))
            l3 = Line(l2 @ 1, (0, block_width))
            l4 = Line(l3 @ 1, (0, 0))
        make_face()
    extrude(amount=block_height)

solid_body = p.part

slot_box = Pos(block_length - slot_depth/2, block_width/2, block_height/2) * Box(slot_depth, slot_width, block_height)
solid_body = solid_body - slot_box

for i in range(2):
    hx = block_length - hole_offset
    hy = block_width/2 + (i - 0.5) * hole_spacing
    solid_body = solid_body - Pos(hx, hy, block_height/2) * Cylinder(hole_diameter/2, block_height)

solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_size)

part = solid_body
part.name = "block_with_slot_and_holes"
export_step(part, "output.step")