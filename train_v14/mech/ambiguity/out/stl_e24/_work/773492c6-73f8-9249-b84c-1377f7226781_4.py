from build123d import *
import math

knob_outer_radius = 30.0
knob_height = 15.0
knob_inner_radius = 8.0
knob_recess_depth = 2.0
knurl_count = 24
knurl_width = 4.0
knurl_height = 6.0
knurl_depth = 2.0

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((knob_inner_radius, 0), (knob_outer_radius, 0))
            l2 = Line(l1@1, (knob_outer_radius, knob_height - knob_recess_depth))
            l3 = Line(l2@1, (knob_inner_radius, knob_height - knob_recess_depth))
            l4 = Line(l3@1, (knob_inner_radius, 0))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part
solid_body = solid_body - Pos(0, 0, knob_height - knob_recess_depth/2) * Cylinder(knob_inner_radius, knob_recess_depth)

for i in range(knurl_count):
    angle = i * 360.0 / knurl_count
    knurl = Rot(0, 0, angle) * Pos(knob_outer_radius + knurl_depth/2, 0, knob_height - knurl_depth/2) * Box(knurl_width, knurl_height, knurl_depth)
    solid_body = solid_body + knurl

part = solid_body
part.name = "knob_with_knurl"
export_step(part, "output.step")