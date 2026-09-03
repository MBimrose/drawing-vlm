from build123d import *
import math

outer_radius = 30.0
inner_radius = 12.0
collar_length = 20.0
fillet_radius = 2.0
slot_width = 6.0
slot_depth = 8.0
slot_center_z = collar_length / 2.0
boss_radius = 5.0
boss_height = 4.0
spline_tooth_width = 3.0
spline_tooth_depth = 2.0
spline_tooth_count = 6

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
solid_body = fillet(solid_body.edges(), fillet_radius)

slot_box = Pos(outer_radius - slot_depth/2, 0, slot_center_z) * Box(slot_depth, slot_width, collar_length)
solid_body = solid_body - slot_box

boss_cyl = Pos(outer_radius - boss_height/2, 0, boss_height/2) * Cylinder(boss_radius, boss_height)
solid_body = solid_body + boss_cyl

for i in range(spline_tooth_count):
    angle = i * 360.0 / spline_tooth_count
    tooth = Rot(0, 0, angle) * Pos(inner_radius - spline_tooth_depth/2, 0, 0) * Box(spline_tooth_depth, spline_tooth_width, collar_length)
    solid_body = solid_body - tooth

part = solid_body
part.name = "collar_with_spline"
export_step(part, "output.step")