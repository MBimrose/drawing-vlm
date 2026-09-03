from build123d import *
import math

inner_diameter = 20.0
outer_diameter = 36.0
collar_length = 30.0
groove_width = 5.0
groove_depth = 2.0
groove_position = 12.0
set_screw_diameter = 2.4
set_screw_offset = 15.0
chamfer_size = 0.5
mount_hole_diameter = 4.0
mount_hole_radius = 14.0
mount_hole_count = 3

inner_radius = inner_diameter / 2.0
outer_radius = outer_diameter / 2.0
wall_thickness = outer_radius - inner_radius

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((inner_radius, 0), (outer_radius, 0))
            l2 = Line(l1@1, (outer_radius, collar_length))
            l3 = Line(l2@1, (inner_radius, collar_length))
            l4 = Line(l3@1, (inner_radius, 0))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part

groove_cyl = Pos(0, 0, groove_position + groove_width / 2) * Cylinder(inner_radius - groove_depth, groove_width)
solid_body = solid_body - groove_cyl

set_screw_cyl = Pos(set_screw_offset, 0, collar_length - wall_thickness / 2) * Cylinder(set_screw_diameter / 2, wall_thickness)
solid_body = solid_body - set_screw_cyl

for i in range(mount_hole_count):
    angle = math.radians(i * 360.0 / mount_hole_count)
    px = mount_hole_radius * math.cos(angle)
    py = mount_hole_radius * math.sin(angle)
    mount_cyl = Pos(px, py, collar_length - wall_thickness / 2) * Cylinder(mount_hole_diameter / 2, wall_thickness + 2)
    solid_body = solid_body - mount_cyl

top_edges = solid_body.edges().sort_by(Axis.Z)[-1:]
solid_body = chamfer(top_edges, chamfer_size)

part = solid_body
part.name = "collar_with_groove_and_holes"
export_step(part, "output.step")