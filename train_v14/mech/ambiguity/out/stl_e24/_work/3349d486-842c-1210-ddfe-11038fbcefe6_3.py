from build123d import *
import math

total_height = 80.0
base_radius = 15.0
top_radius = 30.0
base_height = 15.0
wall_thickness = 3.0
knurl_width = 2.0
knurl_depth = 1.0
knurl_count = 24
chamfer_size = 1.0

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((0, 0), (base_radius, 0))
            l2 = Line(l1@1, (base_radius, base_height))
            l3 = Line(l2@1, (top_radius, total_height))
            l4 = Line(l3@1, (0, total_height))
            l5 = Line(l4@1, (0, 0))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part
top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face])

bottom_edges = solid_body.edges().sort_by(Axis.Z)[:2]
solid_body = chamfer(bottom_edges, chamfer_size)

knurl_r = top_radius - wall_thickness/2
knurl_z = total_height / 2
for i in range(knurl_count):
    angle = math.radians(i * 360.0 / knurl_count)
    px = knurl_r * math.cos(angle)
    py = knurl_r * math.sin(angle)
    knurl_cut = Pos(px, py, knurl_z) * Box(knurl_width, knurl_depth, wall_thickness*2)
    solid_body = solid_body - knurl_cut

part = solid_body
part.name = "knurled_cup"
export_step(part, "output.step")