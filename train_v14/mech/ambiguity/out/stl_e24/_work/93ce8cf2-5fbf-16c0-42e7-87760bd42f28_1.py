from build123d import *
import math

outer_diameter = 50.0
inner_diameter = 12.0
length = 20.0
knurl_width = 10.0
knurl_depth = 1.5
knurl_height = 0.6
knurl_count = 30
chamfer_distance = 0.5
counterbore_diameter = 13.5
counterbore_depth = 4.0

outer_radius = outer_diameter / 2.0
inner_radius = inner_diameter / 2.0
knurl_start_z = (length - knurl_width) / 2.0

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((outer_radius, 0), (outer_radius, length))
            l2 = Line(l1@1, (inner_radius, length))
            l3 = Line(l2@1, (inner_radius, 0))
            l4 = Line(l3@1, (outer_radius, 0))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part

solid_body = solid_body - Pos(0, 0, counterbore_depth/2) * Cylinder(counterbore_diameter/2, counterbore_depth)

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = chamfer(top_face.edges(), chamfer_distance)

for i in range(knurl_count):
    angle = math.radians(i * 360.0 / knurl_count)
    px = (outer_radius - knurl_depth / 2.0) * math.cos(angle)
    py = (outer_radius - knurl_depth / 2.0) * math.sin(angle)
    pz = knurl_start_z + knurl_height / 2.0
    cut_box = Pos(px, py, pz) * Rot(0, 0, math.degrees(angle)) * Box(knurl_depth, knurl_width, knurl_height)
    solid_body = solid_body - cut_box

part = solid_body
part.name = "knurled_bushing"
export_step(part, "output.step")