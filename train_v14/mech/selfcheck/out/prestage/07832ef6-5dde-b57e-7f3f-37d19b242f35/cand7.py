from build123d import *
import math

shaft_radius = 8.0
shaft_length = 60.0
flange_outer_radius = 38.0
flange_thickness = 20.0
keyway_width = 6.0
keyway_depth = 4.0
bolt_hole_diameter = 5.0
bolt_circle_radius = 20.0
bolt_count = 4
pocket_width = 30.0
pocket_length = 20.0
pocket_depth = 8.0
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
total_height = shaft_length + flange_thickness

keyway_box = Pos(shaft_radius - keyway_depth / 2, 0, shaft_length / 2) * Box(keyway_depth, keyway_width, shaft_length)
solid_body = solid_body - keyway_box

for i in range(bolt_count):
    angle = math.radians(i * 360.0 / bolt_count)
    px = bolt_circle_radius * math.cos(angle)
    py = bolt_circle_radius * math.sin(angle)
    hole = Pos(px, py, total_height - flange_thickness / 2) * Cylinder(bolt_hole_diameter / 2, flange_thickness)
    solid_body = solid_body - hole

pocket_box = Pos(0, 0, total_height - pocket_depth / 2) * Box(pocket_width, pocket_length, pocket_depth)
solid_body = solid_body - pocket_box

top_edges = solid_body.edges().sort_by(Axis.Z)[-1:]
solid_body = chamfer(top_edges, chamfer_size)

part = solid_body
part.name = "shaft_with_flange"
export_step(part, "output.step")