from build123d import *

block_length = 100
block_width = 40
block_thickness = 12
rib_height = 3
rib_width = 10
rib_thickness = 3
hole_diameter = 5
hole_spacing_x = 20
hole_spacing_y = 12
hole_rows = 2
hole_cols = 4
chamfer_distance = 1

with BuildPart() as p:
    with BuildSketch() as s:
        Rectangle(block_length, block_width)
    extrude(amount=block_thickness)

solid_body = p.part

rib = Pos(0, 0, -rib_height/2) * Box(rib_width, rib_thickness, rib_height)
solid_body = solid_body + rib

for i in range(hole_cols):
    for j in range(hole_rows):
        x = (i - (hole_cols - 1) / 2) * hole_spacing_x
        y = (j - (hole_rows - 1) / 2) * hole_spacing_y
        solid_body = solid_body - Pos(x, y, block_thickness/2) * Cylinder(hole_diameter/2, block_thickness + rib_height + 10)

right_face = solid_body.faces().sort_by(Axis.X)[-1]
right_edges = right_face.edges()
solid_body = chamfer(right_edges, chamfer_distance)

part = solid_body
part.name = "ribbed_block_with_holes"
export_step(part, "output.step")