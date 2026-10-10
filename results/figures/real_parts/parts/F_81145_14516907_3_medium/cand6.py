from build123d import *
import math

outer_diameter = 80.0
inner_diameter = 45.7
collar_thickness = 15.0
shaft_diameter = 14.3
shaft_length = 40.0
slot_width = 5.0
slot_depth = 12.0
slot_count = 4
chamfer_size = 0.5

outer_radius = outer_diameter / 2.0
inner_radius = inner_diameter / 2.0
shaft_radius = shaft_diameter / 2.0

with BuildPart() as p:
    with BuildSketch(Plane.XY) as sk:
        with BuildLine() as bl:
            l1 = Line((0, 0), (outer_radius, 0))
            l2 = Line(l1 @ 1, (outer_radius, collar_thickness))
            l3 = Line(l2 @ 1, (inner_radius, collar_thickness))
            l4 = Line(l3 @ 1, (inner_radius, 0))
            l5 = Line(l4 @ 1, (0, 0))
        make_face()
    revolve(axis=Axis.Y)

solid_body = p.part
solid_body = solid_body + Pos(0, collar_thickness + shaft_length / 2, 0) * Rot(90, 0, 0) * Cylinder(shaft_radius, shaft_length)

for i in range(slot_count):
    angle = i * 360.0 / slot_count
    slot = Rot(0, angle, 0) * Pos(outer_radius - slot_depth / 2, collar_thickness / 2, 0) * Box(slot_depth, collar_thickness, slot_width)
    solid_body = solid_body - slot

top_face = solid_body.faces().sort_by(Axis.Y)[-1]
solid_body = chamfer(top_face.edges(), chamfer_size)

part = solid_body
part.name = "collar_with_shaft_and_slots"
export_step(part, "output.step")