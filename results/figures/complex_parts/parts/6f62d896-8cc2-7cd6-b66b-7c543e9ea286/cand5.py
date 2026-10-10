from build123d import *
import math

outer_diameter = 80.0
inner_diameter = 30.0
thickness = 10.0
wall_thickness = 2.9
knurl_height = 1.5
knurl_width = 2.0
knurl_count = 24
central_hole_diameter = 8.0
chamfer_distance = 0.5

outer_radius = outer_diameter / 2.0
inner_radius = inner_diameter / 2.0

with BuildPart() as p:
    with BuildSketch() as s:
        Circle(outer_radius)
        Circle(inner_radius)
    extrude(amount=thickness)

solid_body = p.part
solid_body = offset(solid_body, amount=-wall_thickness)

solid_body = solid_body - Pos(0, 0, thickness / 2) * Cylinder(central_hole_diameter / 2, thickness)

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
top_edges = top_face.edges()
solid_body = chamfer(top_edges, chamfer_distance)

knurl_radius = outer_radius - wall_thickness / 2.0
for i in range(knurl_count):
    angle = math.radians(i * 360.0 / knurl_count)
    px = knurl_radius * math.cos(angle)
    py = knurl_radius * math.sin(angle)
    knurl = Pos(px, py, thickness / 2) * Cylinder(knurl_height / 2, thickness)
    solid_body = solid_body + knurl

part = solid_body
part.name = "knurled_ring"
export_step(part, "output.step")