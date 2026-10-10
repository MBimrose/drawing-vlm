from build123d import *
import math

knob_outer_radius = 30.0
knob_height = 12.0
shaft_radius = 8.0
shaft_height = 18.0
central_hole_radius = 8.0
peripheral_hole_radius = 2.0
peripheral_hole_count = 12
peripheral_hole_offset = knob_outer_radius - 4.0
fillet_radius = 3.0
chamfer_distance = 0.8

with BuildPart() as p:
    with BuildSketch() as s:
        Circle(knob_outer_radius)
    extrude(amount=knob_height)

solid_body = p.part

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = fillet(top_face.edges(), fillet_radius)

solid_body = solid_body - Pos(0, 0, knob_height/2) * Cylinder(central_hole_radius, knob_height)

for i in range(peripheral_hole_count):
    angle = math.radians(i * 360.0 / peripheral_hole_count)
    px = peripheral_hole_offset * math.cos(angle)
    py = peripheral_hole_offset * math.sin(angle)
    solid_body = solid_body - Pos(px, py, knob_height/2) * Cylinder(peripheral_hole_radius, knob_height)

shaft = Pos(0, 0, knob_height + shaft_height/2) * Cylinder(shaft_radius, shaft_height)
solid_body = solid_body + shaft

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = chamfer(top_face.edges(), chamfer_distance)

part = solid_body
part.name = "knob"
export_step(part, "output.step")