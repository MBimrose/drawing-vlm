from build123d import *

block_length = 80.0
block_width = 40.0
block_thickness = 10.0
rib_height = 8.0
rib_base_width = 6.0
rib_top_width = 3.0
rib_spacing = 12.0
rib_count = 6
hole_diameter = 5.0
hole_offset = 32.0
chamfer_distance = 0.5

with BuildPart() as p:
    Box(block_length, block_width, block_thickness)
    for i in range(rib_count):
        x = (i - (rib_count - 1) / 2) * rib_spacing
        with Locations(Pos(x, 0, block_thickness / 2)):
            with BuildSketch() as s1:
                Rectangle(rib_base_width, rib_base_width)
            with BuildSketch(Plane.XY.offset(rib_height)) as s2:
                Rectangle(rib_top_width, rib_top_width)
            loft()

solid_body = p.part
for x, y in [(-hole_offset, 0), (0, 0), (hole_offset, 0)]:
    solid_body = solid_body - Pos(x, y, 0) * Cylinder(hole_diameter / 2, 100)

solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_distance)

part = solid_body
part.name = "ribbed_block_with_holes"
export_step(part, "output.step")