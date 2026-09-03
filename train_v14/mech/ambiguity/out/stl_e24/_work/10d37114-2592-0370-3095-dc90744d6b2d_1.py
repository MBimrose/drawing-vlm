from build123d import *

outer_radius = 30.0
inner_radius = 15.0
block_length = 60.0
shoulder_height = 15.0
shoulder_radius = 25.0
fillet_radius = 2.0
hole_diameter = 5.0
hole_offset = 20.0

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((inner_radius, 0), (outer_radius, 0))
            l2 = Line(l1@1, (outer_radius, block_length))
            l3 = Line(l2@1, (shoulder_radius, block_length))
            l4 = Line(l3@1, (shoulder_radius, block_length - shoulder_height))
            l5 = Line(l4@1, (inner_radius, block_length - shoulder_height))
            l6 = Line(l5@1, (inner_radius, 0))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part
solid_body = fillet(solid_body.edges(), fillet_radius)

for x, y in [(hole_offset, 0), (-hole_offset, 0)]:
    solid_body = solid_body - Pos(x, y, block_length/2) * Cylinder(hole_diameter/2, block_length)

part = solid_body
part.name = "revolved_block_with_holes"
export_step(part, "output.step")