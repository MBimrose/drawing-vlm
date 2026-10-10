from build123d import *
import math

outer_radius = 30.0
inner_radius = 20.0
base_height = 10.0
total_height = 25.0
central_hole_radius = 8.0
chamfer_distance = 1.0
mount_hole_radius = 2.5
mount_hole_count = 6
mount_hole_offset = 5.0

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((0, 0), (outer_radius, 0))
            l2 = Line(l1 @ 1, (outer_radius, base_height))
            l3 = Line(l2 @ 1, (inner_radius, base_height))
            l4 = Line(l3 @ 1, (inner_radius, total_height))
            l5 = Line(l4 @ 1, (0, total_height))
            l6 = Line(l5 @ 1, (0, 0))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part
solid_body = solid_body - Pos(0, 0, total_height / 2) * Cylinder(central_hole_radius, total_height)

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = chamfer(top_face.edges(), chamfer_distance)

mount_radius = outer_radius - mount_hole_offset
for i in range(mount_hole_count):
    angle = math.radians(i * 360.0 / mount_hole_count)
    px = mount_radius * math.cos(angle)
    py = mount_radius * math.sin(angle)
    solid_body = solid_body - Pos(px, py, total_height / 2) * Cylinder(mount_hole_radius, total_height)

part = solid_body
part.name = "stepped_cylinder_with_holes"
export_step(part, "output.step")