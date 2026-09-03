from build123d import *
import math

outer_diameter = 50.0
outer_radius = outer_diameter / 2.0
knob_length = 30.0
bore_diameter = 12.0
bore_radius = bore_diameter / 2.0
thread_pitch = 2.0
thread_depth = 0.8
knurl_height = 5.0
knurl_thickness = 2.0
knurl_count = 12
chamfer_size = 0.8
relief_depth = 2.0

with BuildPart() as p:
    with BuildSketch() as s:
        Circle(outer_radius)
    extrude(amount=knob_length)

solid_body = p.part
solid_body = solid_body - Pos(0, 0, knob_length / 2) * Cylinder(bore_radius, knob_length)

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = chamfer(top_face.edges(), chamfer_size)

solid_body = solid_body - Pos(0, 0, knob_length - relief_depth / 2) * Cylinder(bore_radius + 1.0, relief_depth)

for i in range(knurl_count):
    angle = i * 360.0 / knurl_count
    rib = Rot(0, 0, angle) * Pos(outer_radius + knurl_thickness / 2.0, 0, knob_length) * Box(knurl_height, knurl_thickness, knob_length)
    solid_body = solid_body + rib

part = solid_body
part.name = "knob_with_knurl"
export_step(part, "output.step")