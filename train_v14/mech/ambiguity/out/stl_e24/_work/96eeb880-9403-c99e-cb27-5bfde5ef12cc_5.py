from build123d import *

block_length = 80.0
block_width = 50.0
block_thickness = 12.0
corner_chamfer = 5.0
hole_diameter = 6.0
hole_spacing = 25.0
hole_offset = 15.0
rib_width = 6.0
rib_height = 10.0
rib_spacing = 20.0
notch_width = 20.0
notch_depth = 20.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline(
                (-block_length/2, -block_width/2),
                (block_length/2, -block_width/2),
                (block_length/2, block_width/2 - notch_depth),
                (block_length/2 - notch_width, block_width/2),
                (-block_length/2, block_width/2),
                close=True
            )
        make_face()
    extrude(amount=block_thickness)

solid_body = p.part
solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), corner_chamfer)

for x, y in [(-hole_spacing, 0), (0, 0), (hole_spacing, 0)]:
    solid_body = solid_body - Pos(x, y, block_thickness/2) * Cylinder(hole_diameter/2, block_thickness)

rib1 = Pos(-rib_spacing/2, 0, -rib_height/2) * Box(rib_width, block_width - 2*notch_depth, rib_height)
rib2 = Pos(rib_spacing/2, 0, -rib_height/2) * Box(rib_width, block_width - 2*notch_depth, rib_height)
solid_body = solid_body + rib1 + rib2

part = solid_body
part.name = "chamfered_block_with_ribs"
export_step(part, "output.step")