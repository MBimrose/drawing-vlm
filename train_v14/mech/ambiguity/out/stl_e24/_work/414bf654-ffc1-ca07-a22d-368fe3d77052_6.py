from build123d import *
import math

outer_radius = 20.0
wall_thickness = 2.0
inner_radius = outer_radius - wall_thickness
length = 70.0
groove_width = 5.0
groove_depth = 1.5
groove_pitch = 10.0
central_hole_diameter = 10.0
mount_hole_diameter = 4.0
mount_hole_offset = 15.0
chamfer_size = 0.5

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((inner_radius, 0), (outer_radius, 0))
            l2 = Line(l1 @ 1, (outer_radius, length))
            l3 = Line(l2 @ 1, (inner_radius, length))
            l4 = Line(l3 @ 1, (inner_radius, 0))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part
solid_body = solid_body - Cylinder(central_hole_diameter / 2, length)

num_turns = int(length / groove_pitch)
for i in range(num_turns):
    z_pos = i * groove_pitch + groove_pitch / 2
    angle_deg = i * 360.0 / num_turns
    groove = Pos(0, 0, z_pos) * Rot(0, 0, angle_deg) * Pos(inner_radius - groove_depth / 2, 0, 0) * Box(groove_depth, groove_width, groove_depth)
    solid_body = solid_body - groove

for i in range(4):
    angle_deg = i * 90.0
    hole = Rot(0, 0, angle_deg) * Pos(outer_radius - wall_thickness / 2, mount_hole_offset, 0) * Rot(0, 90, 0) * Cylinder(mount_hole_diameter / 2, wall_thickness * 2)
    solid_body = solid_body - hole

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = chamfer(top_face.edges(), chamfer_size)

part = solid_body
part.name = "hollow_cylinder_with_grooves"
export_step(part, "output.step")