from build123d import *

outer_radius = 30.0
inner_radius = 15.0
block_height = 60.0
shoulder_height = 15.0
shoulder_radius = 25.0
fillet_radius = 2.0
mount_hole_diameter = 5.0
mount_hole_offset = 20.0

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((inner_radius, 0), (inner_radius, block_height - shoulder_height))
            l2 = Line(l1@1, (shoulder_radius, block_height - shoulder_height))
            l3 = Line(l2@1, (shoulder_radius, block_height))
            l4 = Line(l3@1, (outer_radius, block_height))
            l5 = Line(l4@1, (outer_radius, 0))
            l6 = Line(l5@1, (inner_radius, 0))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part
solid_body = fillet(solid_body.edges(), fillet_radius)

hole_r = mount_hole_diameter / 2
hole_h = block_height + 10
for x in [mount_hole_offset, -mount_hole_offset]:
    solid_body = solid_body - Pos(x, 0, block_height / 2) * Cylinder(hole_r, hole_h)

part = solid_body
part.name = "revolved_block_with_mount_holes"
export_step(part, "output.step")