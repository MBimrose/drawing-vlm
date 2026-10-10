from build123d import *
import math

knob_outer_radius = 30.0
knob_base_height = 12.0
shaft_radius = 8.0
shaft_height = 18.0
hole_radius = 2.0
hole_count = 12
hole_circle_radius = knob_outer_radius - 4.0
fillet_radius = 3.0
chamfer_distance = 0.8
slot_width = 6.0
slot_length = 12.0
slot_depth = 4.0

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((0, 0), (knob_outer_radius, 0))
            l2 = Line(l1 @ 1, (knob_outer_radius, knob_base_height))
            l3 = Line(l2 @ 1, (shaft_radius, knob_base_height))
            l4 = Line(l3 @ 1, (shaft_radius, knob_base_height + shaft_height))
            l5 = Line(l4 @ 1, (0, knob_base_height + shaft_height))
            l6 = Line(l5 @ 1, (0, 0))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = fillet(top_face.edges(), fillet_radius)

for i in range(hole_count):
    angle = math.radians(i * 360.0 / hole_count)
    px = hole_circle_radius * math.cos(angle)
    py = hole_circle_radius * math.sin(angle)
    solid_body = solid_body - Pos(px, py, 0) * Cylinder(hole_radius, 100)

slot_box = Pos(0, 0, knob_base_height + shaft_height - slot_depth / 2) * Box(slot_width, slot_length, slot_depth)
solid_body = solid_body - slot_box

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = chamfer(top_face.edges(), chamfer_distance)

part = solid_body
part.name = "knob"
export_step(part, "output.step")