from build123d import *
import math

inner_diameter = 20.0
outer_diameter = 36.0
collar_width = 30.0
set_screw_diameter = 2.4
set_screw_head_diameter = 5.0
set_screw_head_depth = 2.0
mount_hole_diameter = 4.0
mount_hole_radius = (outer_diameter / 2) - 4.0
inner_radius = inner_diameter / 2.0
outer_radius = outer_diameter / 2.0

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((inner_radius, 0), (inner_radius, collar_width))
            l2 = Line(l1 @ 1, (outer_radius, collar_width))
            l3 = Line(l2 @ 1, (outer_radius, 0))
            l4 = Line(l3 @ 1, (inner_radius, 0))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part

csk_cone = Pos(0, 0, collar_width - set_screw_head_depth / 2) * Cone(set_screw_head_diameter / 2, set_screw_diameter / 2, set_screw_head_depth)
csk_cyl = Pos(0, 0, collar_width - set_screw_head_depth - (collar_width - set_screw_head_depth) / 2) * Cylinder(set_screw_diameter / 2, collar_width - set_screw_head_depth)
solid_body = solid_body - (csk_cone + csk_cyl)

for i in range(3):
    angle = math.radians(i * 360.0 / 3)
    px = mount_hole_radius * math.cos(angle)
    py = mount_hole_radius * math.sin(angle)
    solid_body = solid_body - Pos(px, py, collar_width - collar_width / 4) * Cylinder(mount_hole_diameter / 2, collar_width / 2)

part = solid_body
part.name = "collar_with_set_screw_and_mount_holes"
export_step(part, "output.step")