from build123d import *

block_length = 80.0
block_width = 50.0
block_thickness = 12.0
corner_chamfer = 5.0
hole_diameter = 6.0
hole_spacing = 25.0
rib_width = 5.0
rib_height = 10.0
rib_length = 40.0
pocket_width = 20.0
pocket_depth = 20.0
pocket_offset = 10.0

with BuildPart() as p:
    with BuildSketch() as s:
        Rectangle(block_length, block_width)
    extrude(amount=block_thickness)

solid_body = p.part
solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), corner_chamfer)

for x, y in [(-hole_spacing, 0), (0, 0), (hole_spacing, 0)]:
    solid_body = solid_body - Pos(x, y, block_thickness/2) * Cylinder(hole_diameter/2, block_thickness + 1)

rib1 = Pos(0, 0, -rib_height/2) * Box(rib_length, rib_width, rib_height)
rib2 = Pos(0, 0, -rib_height/2) * Box(rib_width, rib_length, rib_height)
solid_body = solid_body + rib1 + rib2

pocket = Pos(block_length/2 - pocket_offset, block_width/2 - pocket_offset, block_thickness/2) * Box(pocket_width, pocket_depth, block_thickness)
solid_body = solid_body - pocket

part = solid_body
part.name = "chamfered_block_with_ribs_and_pocket"
export_step(part, "output.step")