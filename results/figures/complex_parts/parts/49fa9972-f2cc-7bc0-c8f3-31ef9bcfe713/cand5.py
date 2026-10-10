from build123d import *

block_length = 60.0
block_width = 40.0
block_height = 20.0
notch_radius = 5.0
pocket_width = 10.0
pocket_length = 15.0
pocket_depth = 5.0
hole_diameter = 6.0
hole_spacing = 24.0
hole_offset = 12.0
chamfer_size = 1.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            l1 = Line((-block_length/2, -block_width/2), (block_length/2 - notch_radius, -block_width/2))
            a1 = ThreePointArc(l1@1, (block_length/2, -block_width/2), (block_length/2, -block_width/2 + notch_radius))
            l2 = Line(a1@1, (block_length/2, block_width/2))
            l3 = Line(l2@1, (-block_length/2, block_width/2))
            l4 = Line(l3@1, (-block_length/2, -block_width/2))
        make_face()
    extrude(amount=block_height)

solid_body = p.part

pocket = Pos(block_length/2 - pocket_depth/2, 0, block_height/2) * Box(pocket_depth, pocket_width, pocket_length)
solid_body = solid_body - pocket

for y in [-hole_spacing/2, hole_spacing/2]:
    hole = Pos(hole_offset, y, block_height/2) * Cylinder(hole_diameter/2, block_height)
    solid_body = solid_body - hole

vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = chamfer(vertical_edges, chamfer_size)

part = solid_body
part.name = "notched_block_with_pocket_and_holes"
export_step(part, "output.step")