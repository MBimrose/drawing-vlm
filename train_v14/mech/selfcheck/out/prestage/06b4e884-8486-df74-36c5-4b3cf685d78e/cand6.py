from build123d import *

block_length = 100.0
block_width = 40.0
block_thickness = 12.0
slot_length = 80.0
slot_width = 6.0
hole_diameter = 5.0
hole_spacing_x = 20.0
hole_spacing_y = 12.0
hole_rows = 2
hole_cols = 4
chamfer_size = 1.0
rib_height = 3.0
rib_width = 10.0
rib_thickness = 3.0

with BuildPart() as p:
    with BuildSketch() as s:
        Rectangle(block_length, block_width)
        Rectangle(slot_length, slot_width, mode=Mode.SUBTRACT)
    extrude(amount=block_thickness)

solid_body = p.part

rib = Pos(0, 0, -rib_height/2) * Box(rib_width, rib_thickness, rib_height)
solid_body = solid_body + rib

for i in range(hole_cols):
    for j in range(hole_rows):
        x = (i - (hole_cols - 1) / 2) * hole_spacing_x
        y = (j - (hole_rows - 1) / 2) * hole_spacing_y
        solid_body = solid_body - Pos(x, y, block_thickness/2) * Cylinder(hole_diameter/2, block_thickness + 10)

right_face = solid_body.faces().sort_by(Axis.X)[-1]
solid_body = chamfer(right_face.edges(), chamfer_size)

part = solid_body
part.name = "block_with_slot_rib_holes"
export_step(part, "output.step")