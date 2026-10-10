from build123d import *
import math

knob_outer_radius = 30.0
knob_height = 12.0
shaft_radius = 8.0
shaft_length = 18.0
hole_diameter = 4.0
hole_count = 12
hole_circle_radius = knob_outer_radius - 4.0
fillet_radius = 3.0
chamfer_distance = 0.8
grip_width = 20.0
grip_depth = 4.0
grip_height = 6.0
slot_width = 6.0
slot_depth = 3.0
slot_height = 4.0

with BuildPart() as p:
    with BuildSketch() as s:
        Circle(knob_outer_radius)
    extrude(amount=knob_height)

solid_body = p.part
top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = fillet(top_face.edges(), fillet_radius)

shaft = Pos(0, 0, knob_height + shaft_length / 2) * Cylinder(shaft_radius, shaft_length)
solid_body = solid_body + shaft

for i in range(hole_count):
    angle = math.radians(i * 360.0 / hole_count)
    px = hole_circle_radius * math.cos(angle)
    py = hole_circle_radius * math.sin(angle)
    hole = Pos(px, py, (knob_height + shaft_length) / 2) * Cylinder(hole_diameter / 2, knob_height + shaft_length + 10)
    solid_body = solid_body - hole

grip = Pos(knob_outer_radius - grip_depth / 2, 0, knob_height / 2) * Box(grip_depth, grip_width, grip_height)
solid_body = solid_body - grip

slot = Pos(shaft_radius - slot_depth / 2, 0, knob_height + shaft_length / 2) * Box(slot_depth, slot_width, slot_height)
solid_body = solid_body - slot

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = chamfer(top_face.edges(), chamfer_distance)

part = solid_body
part.name = "knob"
export_step(part, "output.step")