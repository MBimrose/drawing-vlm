from build123d import *

outer_diameter = 60.0
spacer_height = 15.0
central_hole_diameter = 12.0
central_hole_depth = 10.0
top_recess_depth = 2.0
top_recess_diameter = 30.0
mounting_hole_diameter = 4.0
mounting_hole_offset = 20.0
chamfer_size = 1.0

with BuildPart() as p:
    with BuildSketch() as s:
        Circle(outer_diameter / 2)
    extrude(amount=spacer_height)

solid_body = p.part
solid_body = chamfer(solid_body.edges(), chamfer_size)

solid_body = solid_body - Pos(0, 0, spacer_height - central_hole_depth / 2) * Cylinder(central_hole_diameter / 2, central_hole_depth)

solid_body = solid_body - Pos(0, 0, spacer_height - top_recess_depth / 2) * Cylinder(top_recess_diameter / 2, top_recess_depth)

for x, y in [(mounting_hole_offset, mounting_hole_offset),
             (-mounting_hole_offset, mounting_hole_offset),
             (-mounting_hole_offset, -mounting_hole_offset),
             (mounting_hole_offset, -mounting_hole_offset)]:
    solid_body = solid_body - Pos(x, y, spacer_height / 2) * Cylinder(mounting_hole_diameter / 2, spacer_height)

part = solid_body
part.name = "spacer"
export_step(part, "output.step")