from build123d import *

block_length = 80.0
block_width = 40.0
block_height = 20.0
notch_width = 10.0
notch_depth = 15.0
hole_diameter = 6.0
hole_spacing = 24.0
hole_offset_y = 12.0
chamfer_size = 1.0
fillet_radius = 5.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            l1 = Line((-block_length/2, -block_width/2), (block_length/2 - fillet_radius, -block_width/2))
            a1 = ThreePointArc(l1 @ 1, (block_length/2, -block_width/2), (block_length/2, -block_width/2 + fillet_radius))
            l2 = Line(a1 @ 1, (block_length/2, block_width/2))
            l3 = Line(l2 @ 1, (-block_length/2, block_width/2))
            l4 = Line(l3 @ 1, l1 @ 0)
        make_face()
    extrude(amount=block_height)

solid_body = p.part

notch = Pos(block_length/2 - notch_width/2, 0, block_height/2) * Box(notch_width, notch_depth, block_height)
solid_body = solid_body - notch

for y in [-hole_spacing/2, hole_spacing/2]:
    solid_body = solid_body - Pos(block_length/2 - hole_offset_y, y, block_height/2) * Cylinder(hole_diameter/2, block_height)

solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_size)

part = solid_body
part.name = "notched_block_with_holes"
export_step(part, "output.step")