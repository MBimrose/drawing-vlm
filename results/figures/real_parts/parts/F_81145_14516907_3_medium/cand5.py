from build123d import *
import math

outer_diameter = 80.0
inner_diameter = 30.0
collar_length = 40.0
shoulder_length = 10.0
shoulder_diameter = 50.0
spline_tooth_height = 5.0
spline_tooth_width = 8.0
spline_tooth_count = 6
chamfer_size = 2.0
mount_hole_diameter = 5.0
mount_hole_count = 4
mount_hole_radius = 20.0

outer_radius = outer_diameter / 2.0
inner_radius = inner_diameter / 2.0
shoulder_radius = shoulder_diameter / 2.0

with BuildPart() as p:
    with BuildSketch(Plane.XY) as sk:
        with BuildLine() as bl:
            l1 = Line((0, 0), (outer_radius, 0))
            l2 = Line(l1 @ 1, (outer_radius, shoulder_length))
            l3 = Line(l2 @ 1, (shoulder_radius, shoulder_length))
            l4 = Line(l3 @ 1, (shoulder_radius, collar_length))
            l5 = Line(l4 @ 1, (0, collar_length))
            l6 = Line(l5 @ 1, (0, 0))
        make_face()
    revolve(axis=Axis.Y)

solid_body = p.part
solid_body = solid_body - Pos(0, collar_length / 2, 0) * Rot(90, 0, 0) * Cylinder(inner_radius, collar_length)

for i in range(mount_hole_count):
    angle = math.radians(i * 360.0 / mount_hole_count)
    px = mount_hole_radius * math.cos(angle)
    pz = mount_hole_radius * math.sin(angle)
    solid_body = solid_body - Pos(px, collar_length / 2, pz) * Rot(90, 0, 0) * Cylinder(mount_hole_diameter / 2, collar_length)

for i in range(spline_tooth_count):
    angle = math.radians(i * 360.0 / spline_tooth_count)
    tooth = Rot(0, angle, 0) * Pos(inner_radius - spline_tooth_height / 2, collar_length / 2, 0) * Box(spline_tooth_height, collar_length, spline_tooth_width)
    solid_body = solid_body - tooth

top_face = solid_body.faces().sort_by(Axis.Y)[-1]
solid_body = chamfer(top_face.edges(), chamfer_size)

part = solid_body
part.name = "spline_collar"
export_step(part, "output.step")