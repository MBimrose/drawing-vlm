from build123d import *
import math

outer_radius = 30.0
shoulder_radius = 20.0
base_thickness = 10.0
shoulder_height = 15.0
central_bore_radius = 8.0
hole_diameter = 5.0
hole_count = 6
hole_circle_radius = 25.0
chamfer_distance = 1.0

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((0, 0), (outer_radius, 0))
            l2 = Line(l1 @ 1, (outer_radius, base_thickness))
            l3 = Line(l2 @ 1, (shoulder_radius, base_thickness))
            l4 = Line(l3 @ 1, (shoulder_radius, base_thickness + shoulder_height))
            l5 = Line(l4 @ 1, (0, base_thickness + shoulder_height))
            l6 = Line(l5 @ 1, (0, 0))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part

total_height = base_thickness + shoulder_height
solid_body = solid_body - Pos(0, 0, total_height / 2) * Cylinder(central_bore_radius, total_height + 10)

for i in range(hole_count):
    angle = math.radians(i * 360.0 / hole_count)
    px = hole_circle_radius * math.cos(angle)
    py = hole_circle_radius * math.sin(angle)
    solid_body = solid_body - Pos(px, py, total_height / 2) * Cylinder(hole_diameter / 2, total_height + 10)

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
top_edges = top_face.edges()
solid_body = chamfer(top_edges, chamfer_distance)

part = solid_body
part.name = "stepped_cylinder_with_holes"
export_step(part, "output.step")