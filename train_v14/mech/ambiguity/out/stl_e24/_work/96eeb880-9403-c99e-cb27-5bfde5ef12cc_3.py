from build123d import *

block_length = 80.0
block_width = 50.0
block_thickness = 12.0
bevel_distance = 15.0
hole_diameter = 6.0
hole_spacing = 25.0
chamfer_distance = 5.0
rib_width = 6.0
rib_height = 4.0
rib_spacing = 20.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline(
                (-block_length/2, -block_width/2),
                (block_length/2, -block_width/2),
                (block_length/2, block_width/2 - bevel_distance),
                (block_length/2 - bevel_distance, block_width/2),
                (-block_length/2, block_width/2),
                close=True
            )
        make_face()
    extrude(amount=block_thickness)

solid_body = p.part
solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_distance)

for x, y in [(-hole_spacing, 0), (0, 0), (hole_spacing, 0)]:
    solid_body = solid_body - Pos(x, y, 0) * Cylinder(hole_diameter/2, block_thickness * 2)

for x, y in [(-rib_spacing/2, 0), (rib_spacing/2, 0)]:
    solid_body = solid_body + Pos(x, y, -rib_height/2) * Box(rib_width, rib_height, rib_height)

part = solid_body
part.name = "beveled_block_with_holes_and_ribs"
export_step(part, "output.step")