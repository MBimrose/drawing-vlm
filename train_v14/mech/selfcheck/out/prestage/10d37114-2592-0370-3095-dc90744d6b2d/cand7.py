from build123d import *

outer_radius = 30
inner_radius = 15
block_length = 60
groove_width = 10
groove_depth = 5
groove_start = 20
fillet_radius = 2
hole_diameter = 5
hole_offset = 20

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((inner_radius, 0), (outer_radius, 0))
            l2 = Line(l1@1, (outer_radius, block_length))
            l3 = Line(l2@1, (outer_radius - groove_depth, block_length))
            l4 = Line(l3@1, (outer_radius - groove_depth, groove_start + groove_width))
            l5 = Line(l4@1, (inner_radius, groove_start + groove_width))
            l6 = Line(l5@1, (inner_radius, 0))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part
solid_body = fillet(solid_body.edges(), fillet_radius)

for x, y in [(hole_offset, 0), (-hole_offset, 0)]:
    solid_body = solid_body - Pos(x, y, block_length/2) * Cylinder(hole_diameter/2, block_length)

part = solid_body
part.name = "revolved_block_with_groove_and_holes"
export_step(part, "output.step")