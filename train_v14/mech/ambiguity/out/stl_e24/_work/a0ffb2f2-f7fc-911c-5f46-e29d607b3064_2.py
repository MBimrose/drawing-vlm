from build123d import *

shaft_radius = 5
shaft_length = 60
flange_radius = 15
flange_thickness = 10
bore_radius = 4
bore_depth = 45
keyway_width = 4
keyway_depth = 2
keyway_length = 30
chamfer_size = 1
mount_hole_radius = 2
mount_hole_spacing = 30

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((0, 0), (shaft_radius, 0))
            l2 = Line(l1 @ 1, (shaft_radius, shaft_length - flange_thickness))
            l3 = Line(l2 @ 1, (flange_radius, shaft_length - flange_thickness))
            l4 = Line(l3 @ 1, (flange_radius, shaft_length))
            l5 = Line(l4 @ 1, (0, shaft_length))
            l6 = Line(l5 @ 1, (0, 0))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part
solid_body = solid_body - Pos(0, 0, shaft_length - bore_depth / 2) * Cylinder(bore_radius, bore_depth)
solid_body = solid_body - Pos(shaft_radius - keyway_depth / 2, 0, shaft_length / 2) * Box(keyway_depth, keyway_width, keyway_length)
top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = chamfer(top_face.edges(), chamfer_size)
for x, y in [(-mount_hole_spacing / 2, 0), (mount_hole_spacing / 2, 0)]:
    solid_body = solid_body - Pos(x, y, shaft_length / 2) * Cylinder(mount_hole_radius, shaft_length + 20)

part = solid_body
part.name = "shaft_with_flange"
export_step(part, "output.step")