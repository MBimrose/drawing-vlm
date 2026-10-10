from build123d import *

block_length = 60.0
block_width = 40.0
block_height = 20.0
corner_radius = 5.0
notch_width = 10.0
notch_depth = 5.0
hole_diameter = 6.0
hole_spacing_x = 30.0
hole_spacing_y = 20.0
chamfer_size = 1.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            l1 = Line((0, 0), (block_length - corner_radius, 0))
            a1 = ThreePointArc(l1 @ 1, (block_length, 0), (block_length, corner_radius))
            l2 = Line(a1 @ 1, (block_length, block_width))
            l3 = Line(l2 @ 1, (0, block_width))
            l4 = Line(l3 @ 1, (0, 0))
        make_face()
    extrude(amount=block_height)

solid_body = p.part

notch = Pos(block_length - notch_depth/2, block_width/2, block_height/2) * Box(notch_depth, notch_width, block_height)
solid_body = solid_body - notch

for i in range(2):
    for j in range(2):
        hx = block_length/2 + (i - 0.5) * hole_spacing_x
        hy = block_width/2 + (j - 0.5) * hole_spacing_y
        solid_body = solid_body - Pos(hx, hy, block_height/2) * Cylinder(hole_diameter/2, block_height)

vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = chamfer(vertical_edges, chamfer_size)

part = solid_body
part.name = "block_with_notch_and_holes"
export_step(part, "output.step")