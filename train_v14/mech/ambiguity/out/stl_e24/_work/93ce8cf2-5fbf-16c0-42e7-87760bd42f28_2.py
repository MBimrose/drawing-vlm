from build123d import *
import math

outer_diameter = 50.0
outer_radius = outer_diameter / 2.0
knob_height = 20.0
shaft_diameter = 12.0
shaft_radius = shaft_diameter / 2.0
knurl_depth = 1.5
knurl_width = 2.0
knurl_count = 30
chamfer_size = 0.8
set_screw_diameter = 3.0
set_screw_depth = 4.0
set_screw_offset = 5.0
counterbore_diameter = shaft_diameter + 1.5
counterbore_depth = 2.0

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((shaft_radius, 0), (shaft_radius, knob_height))
            l2 = Line(l1 @ 1, (outer_radius, knob_height))
            l3 = Line(l2 @ 1, (outer_radius, 0))
            l4 = Line(l3 @ 1, (shaft_radius, 0))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part

top_edges = solid_body.edges().sort_by(Axis.Z)[-1:]
solid_body = chamfer(top_edges, chamfer_size)

solid_body = solid_body - Pos(0, 0, counterbore_depth/2) * Cylinder(counterbore_diameter/2, counterbore_depth)

for i in range(knurl_count):
    angle = math.radians(i * 360.0 / knurl_count)
    px = (outer_radius - knurl_depth/2) * math.cos(angle)
    py = (outer_radius - knurl_depth/2) * math.sin(angle)
    knurl_box = Pos(px, py, knob_height/2) * Rot(0, 0, math.degrees(angle)) * Box(knurl_depth, knurl_width, knurl_depth)
    solid_body = solid_body - knurl_box

set_screw = Pos(outer_radius - set_screw_offset, 0, knob_height - set_screw_depth/2) * Cylinder(set_screw_diameter/2, set_screw_depth)
solid_body = solid_body - set_screw

part = solid_body
part.name = "knob"
export_step(part, "output.step")