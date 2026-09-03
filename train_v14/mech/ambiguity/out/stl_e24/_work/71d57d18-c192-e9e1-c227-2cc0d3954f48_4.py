from build123d import *
import math

outer_radius = 30.0
inner_radius = 12.0
knob_height = 20.0
shoulder_height = 5.0
shoulder_radius = 22.0
chamfer_dist = 2.0
mount_hole_dia = 4.0
mount_hole_offset = 18.0
boss_radius = 4.0
boss_height = 6.0
boss_offset = 10.0

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((inner_radius, 0), (outer_radius, 0))
            l2 = Line(l1@1, (outer_radius, knob_height - shoulder_height))
            a1 = ThreePointArc(l2@1, (outer_radius - 2, knob_height - shoulder_height + 2), (shoulder_radius, knob_height))
            l3 = Line(a1@1, (inner_radius, knob_height))
            l4 = Line(l3@1, (inner_radius, 0))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part
solid_body = chamfer(solid_body.edges(), chamfer_dist)

for x, y in [(-mount_hole_offset, 0), (mount_hole_offset, 0)]:
    solid_body = solid_body - Pos(x, y, knob_height/2) * Cylinder(mount_hole_dia/2, knob_height + 10)

boss = Pos(boss_offset, 0, 0) * Rot(0, 90, 0) * Cylinder(boss_radius, boss_height)
solid_body = solid_body + boss

part = solid_body
part.name = "knob_with_boss"
export_step(part, "output.step")