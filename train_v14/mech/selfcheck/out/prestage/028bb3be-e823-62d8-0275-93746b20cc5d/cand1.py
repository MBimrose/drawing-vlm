from build123d import *
import math

outer_diameter = 80.0
inner_diameter = 30.0
collar_length = 20.0
set_screw_diameter = 2.0
set_screw_offset = 12.0
chamfer_distance = 1.0
knurl_height = 4.0
knurl_width = 6.0
knurl_count = 12
groove_width = 4.0
groove_depth = 2.0
groove_length = 12.0

outer_radius = outer_diameter / 2.0
inner_radius = inner_diameter / 2.0

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

top_edges = solid_body.edges().sort_by(Axis.Z)[-1:]
solid_body = chamfer(top_edges, chamfer_distance)

solid_body = solid_body - Pos(inner_radius + set_screw_offset, 0, collar_length/2) * Cylinder(set_screw_diameter/2, collar_length)

solid_body = solid_body - Pos(inner_radius - groove_depth/2, 0, collar_length/2) * Box(groove_depth, groove_width, groove_length)

for i in range(knurl_count):
    angle = i * 360.0 / knurl_count
    knurl = Pos(outer_radius + knurl_height/2, 0, collar_length) * Rot(0, 0, angle) * Box(knurl_width, knurl_height, collar_length)
    solid_body = solid_body + knurl

part = solid_body
part.name = "knurled_collar"
export_step(part, "output.step")