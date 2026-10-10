from build123d import *
import math

shaft_radius = 8.0
shaft_length = 60.0
flange_thickness = 20.0
flange_outer_radius = 38.0
keyway_width = 6.0
keyway_depth = 4.0
keyway_length = 30.0
hole_diameter = 5.0
hole_count = 4
hole_circle_radius = 20.0
chamfer_size = 1.0

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((0, 0), (shaft_radius, 0))
            l2 = Line(l1 @ 1, (shaft_radius, shaft_length))
            l3 = Line(l2 @ 1, (flange_outer_radius, shaft_length))
            l4 = Line(l3 @ 1, (flange_outer_radius, shaft_length + flange_thickness))
            l5 = Line(l4 @ 1, (0, shaft_length + flange_thickness))
            l6 = Line(l5 @ 1, (0, 0))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part

keyway_box = Pos(shaft_radius - keyway_depth / 2, shaft_length / 2, 0) * Box(keyway_depth, keyway_width, keyway_length)
solid_body = solid_body - keyway_box

for i in range(hole_count):
    angle = math.radians(i * 360.0 / hole_count)
    px = hole_circle_radius * math.cos(angle)
    py = hole_circle_radius * math.sin(angle)
    hole = Pos(px, py, shaft_length + flange_thickness / 2) * Cylinder(hole_diameter / 2, flange_thickness)
    solid_body = solid_body - hole

top_edges = solid_body.edges().sort_by(Axis.Z)[-1:]
solid_body = chamfer(top_edges, chamfer_size)

part = solid_body
part.name = "shaft_with_flange"
export_step(part, "output.step")