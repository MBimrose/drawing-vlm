from build123d import *
import math

body_diameter = 80
body_length = 100
shaft_diameter = 30
inlet_diameter = 40
inlet_center_offset = 30
inlet_depth = 20
inlet_chamfer = 2
relief_start = 40
relief_end = 60
relief_radius = 45
relief_cavity_diameter = 60
relief_cavity_depth = 10

body_radius = body_diameter / 2.0
shaft_radius = shaft_diameter / 2.0

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((0, 0), (body_radius, 0))
            l2 = Line(l1@1, (body_radius, relief_start))
            l3 = Line(l2@1, (relief_radius, relief_start))
            l4 = Line(l3@1, (relief_radius, relief_end))
            l5 = Line(l4@1, (body_radius, relief_end))
            l6 = Line(l5@1, (body_radius, body_length))
            l7 = Line(l6@1, (shaft_radius, body_length))
            l8 = Line(l7@1, (shaft_radius, 0))
            l9 = Line(l8@1, (0, 0))
        make_face()
    revolve(axis=Axis.Z)

solid = p.part
solid = solid - Pos(0, 0, body_length / 2) * Cylinder(shaft_radius, body_length)
inlet_z = (relief_start + relief_end) / 2
inlet_cyl = Rot(0, 90, 0) * Cylinder(inlet_diameter / 2, inlet_depth)
solid = solid - Pos(relief_radius - inlet_depth / 2, inlet_center_offset, inlet_z) * inlet_cyl
solid = chamfer(solid.edges(), inlet_chamfer)
solid = solid - Pos(0, 0, body_length - relief_cavity_depth / 2) * Cylinder(relief_cavity_diameter / 2, relief_cavity_depth)

part = solid
part.name = "revolved_body_with_inlet"
export_step(part, OUTPUT_PATH)