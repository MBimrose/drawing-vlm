from build123d import *

total_length = 80.0
base_radius = 25.0
top_radius = 10.0
central_hole_dia = 8.0
mount_hole_dia = 4.0
mount_hole_spacing = 30.0
pocket_width = 12.0
pocket_height = 6.0
pocket_depth = 4.0
relief_radius = 6.0
relief_depth = 2.0
chamfer_size = 0.5

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((0, 0), (base_radius, 0))
            l2 = Line(l1 @ 1, (top_radius, total_length))
            l3 = Line(l2 @ 1, (0, total_length))
            l4 = Line(l3 @ 1, (0, 0))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part

solid_body = solid_body - Pos(0, 0, total_length / 2) * Cylinder(central_hole_dia / 2, total_length + 10)

for x in [-mount_hole_spacing / 2, mount_hole_spacing / 2]:
    solid_body = solid_body - Pos(x, 0, total_length / 2) * Rot(90, 0, 0) * Cylinder(mount_hole_dia / 2, total_length + 10)

solid_body = solid_body - Pos(0, 0, total_length / 2 + pocket_depth / 2) * Box(pocket_width, pocket_height, pocket_depth)

solid_body = solid_body - Pos(0, 0, total_length - relief_depth / 2) * Cylinder(relief_radius, relief_depth)

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = chamfer(top_face.edges(), chamfer_size)

part = solid_body
part.name = "tapered_cone_with_holes"
export_step(part, "output.step")