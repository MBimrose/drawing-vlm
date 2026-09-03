from build123d import *
import math

outer_diameter = 50.0
inner_diameter = 12.0
collar_length = 20.0
counterbore_diameter = 13.5
counterbore_depth = 5.0
knurl_count = 24
knurl_width = 1.5
knurl_depth = 0.6
knurl_height = 2.0
chamfer_size = 0.8

outer_radius = outer_diameter / 2.0
inner_radius = inner_diameter / 2.0
counterbore_radius = counterbore_diameter / 2.0

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            Polyline((outer_radius, 0), (outer_radius, collar_length), (inner_radius, collar_length), (inner_radius, 0), close=True)
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = chamfer(top_face.edges(), chamfer_size)

solid_body = solid_body - Pos(0, 0, counterbore_depth/2) * Cylinder(counterbore_radius, counterbore_depth)

for i in range(knurl_count):
    angle = i * 360.0 / knurl_count
    groove = Rot(0, 0, angle) * Pos(outer_radius - knurl_depth/2, 0, collar_length/2) * Box(knurl_depth, knurl_height, knurl_width)
    solid_body = solid_body - groove

part = solid_body
part.name = "knurled_collar"
export_step(part, "output.step")